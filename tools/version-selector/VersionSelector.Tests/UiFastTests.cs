using System.Text.Json;
using FlaUI.Core.AutomationElements;
using FlaUI.Core.Definitions;
using FlaUI.Core.Tools;
using Xunit;

namespace VersionSelector.Tests;

// All UI tests share one collection so FlaUI/WinForms automation across
// separate launched processes never runs concurrently on this machine.
[CollectionDefinition("UI Tests", DisableParallelization = true)]
public class UiTestCollection { }

/// <summary>
/// Fast suite: every test here runs the real compiled EXE and drives it
/// through real UI Automation (FlaUI/UIA3), but with VERSION_SELECTOR_FAKE_DOCKER_STATE
/// set so it never touches real Docker -- deterministic, no Docker Desktop
/// dependency, safe to run anywhere including CI. The one true end-to-end
/// test that starts/stops a real mock instance lives in UiSlowEndToEndTests.
/// </summary>
[Collection("UI Tests")]
public class UiFastTests
{
    private static string Fixture(string name) => Path.Combine(AppContext.BaseDirectory, "Fixtures", name);

    private static string NewTempLogPath()
    {
        var path = Path.Combine(Path.GetTempPath(), $"version-selector-test-log-{Guid.NewGuid():N}.jsonl");
        return path;
    }

    [Fact]
    public void Launch_ShowsMainWindow_PopulatedFromRegistry()
    {
        using var testApp = UiTestApp.Launch(new Dictionary<string, string>
        {
            ["VERSION_SELECTOR_REGISTRY"] = Fixture("ui-fast-registry.json"),
            ["VERSION_SELECTOR_FAKE_DOCKER_STATE"] = Fixture("ui-fast-docker-state-mixed.json"),
        });

        Assert.Contains("Version Selector", testApp.MainWindow.Title);

        var listView = testApp.MainWindow.FindFirstDescendant(cf => cf.ByAutomationId(AutomationIds.VersionsListView));
        Assert.NotNull(listView);

        var rows = listView!.GetListViewRows();
        Assert.Equal(2, rows.Count);
        Assert.Equal("v1.1 (stable)", rows[0][0]);
        Assert.Equal("v1.2-dev", rows[1][0]);

        foreach (var id in new[] { AutomationIds.StartButton, AutomationIds.StopButton, AutomationIds.RestartButton, AutomationIds.RefreshButton })
        {
            var button = testApp.MainWindow.FindFirstDescendant(cf => cf.ByAutomationId(id));
            Assert.NotNull(button);
        }

        var messageLabel = testApp.MainWindow.FindFirstDescendant(cf => cf.ByAutomationId(AutomationIds.MessageLabel));
        Assert.NotNull(messageLabel);
    }

    [Fact]
    public void StatusColumn_ReflectsMockedDockerPsResponse()
    {
        using var testApp = UiTestApp.Launch(new Dictionary<string, string>
        {
            ["VERSION_SELECTOR_REGISTRY"] = Fixture("ui-fast-registry.json"),
            ["VERSION_SELECTOR_FAKE_DOCKER_STATE"] = Fixture("ui-fast-docker-state-mixed.json"),
        });

        var listView = testApp.MainWindow.FindFirstDescendant(cf => cf.ByAutomationId(AutomationIds.VersionsListView))!;
        var rows = listView.GetListViewRows();

        Assert.Equal("Running", rows[0][1]);  // mock-v11, seeded Running
        Assert.Equal("Stopped", rows[1][1]);  // mock-v12-dev, seeded Stopped
    }

    [Fact]
    public void ClickingStart_InvokesComposeUp_ForSelectedVersion()
    {
        var logPath = NewTempLogPath();
        using var testApp = UiTestApp.Launch(new Dictionary<string, string>
        {
            ["VERSION_SELECTOR_REGISTRY"] = Fixture("ui-fast-registry.json"),
            ["VERSION_SELECTOR_FAKE_DOCKER_STATE"] = Fixture("ui-fast-docker-state-mixed.json"),
            ["VERSION_SELECTOR_FAKE_DOCKER_LOG"] = logPath,
        });

        var listView = testApp.MainWindow.FindFirstDescendant(cf => cf.ByAutomationId(AutomationIds.VersionsListView))!;
        listView.SelectListViewRow(1);

        var startButton = testApp.MainWindow.FindFirstDescendant(cf => cf.ByAutomationId(AutomationIds.StartButton))!.AsButton();
        startButton.Invoke();

        Retry.WhileFalse(() => File.Exists(logPath) && File.ReadAllText(logPath).Length > 0,
            timeout: TimeSpan.FromSeconds(10));

        var line = File.ReadAllLines(logPath).Single();
        using var doc = JsonDocument.Parse(line);
        Assert.Equal("mock-v12-dev", doc.RootElement.GetProperty("ComposeProject").GetString());
        Assert.Equal("Up", doc.RootElement.GetProperty("Action").GetString());
        Assert.Equal(@"C:\fake\RESTful-API-Integration", doc.RootElement.GetProperty("WorkingDirectory").GetString());

        var messageLabel = testApp.MainWindow.FindFirstDescendant(cf => cf.ByAutomationId(AutomationIds.MessageLabel))!;
        Retry.WhileFalse(() => messageLabel.Name.Contains("succeeded"), timeout: TimeSpan.FromSeconds(5));
    }

    [Fact]
    public void ClickingStop_InvokesComposeDown_ForSelectedVersion()
    {
        var logPath = NewTempLogPath();
        using var testApp = UiTestApp.Launch(new Dictionary<string, string>
        {
            ["VERSION_SELECTOR_REGISTRY"] = Fixture("ui-fast-registry.json"),
            ["VERSION_SELECTOR_FAKE_DOCKER_STATE"] = Fixture("ui-fast-docker-state-mixed.json"),
            ["VERSION_SELECTOR_FAKE_DOCKER_LOG"] = logPath,
        });

        var listView = testApp.MainWindow.FindFirstDescendant(cf => cf.ByAutomationId(AutomationIds.VersionsListView))!;
        listView.SelectListViewRow(0);

        var stopButton = testApp.MainWindow.FindFirstDescendant(cf => cf.ByAutomationId(AutomationIds.StopButton))!.AsButton();
        stopButton.Invoke();

        Retry.WhileFalse(() => File.Exists(logPath) && File.ReadAllText(logPath).Length > 0,
            timeout: TimeSpan.FromSeconds(10));

        var line = File.ReadAllLines(logPath).Single();
        using var doc = JsonDocument.Parse(line);
        Assert.Equal("mock-v11", doc.RootElement.GetProperty("ComposeProject").GetString());
        Assert.Equal("Down", doc.RootElement.GetProperty("Action").GetString());
    }

    [Fact]
    public void DockerUnavailable_ShowsErrorMessage_WithoutCrashing()
    {
        using var testApp = UiTestApp.Launch(new Dictionary<string, string>
        {
            ["VERSION_SELECTOR_REGISTRY"] = Fixture("ui-fast-registry.json"),
            ["VERSION_SELECTOR_FAKE_DOCKER_STATE"] = Fixture("ui-fast-docker-state-unavailable.json"),
        });

        var messageLabel = testApp.MainWindow.FindFirstDescendant(cf => cf.ByAutomationId(AutomationIds.MessageLabel))!;
        Retry.WhileFalse(() => messageLabel.Name.Contains("Docker does not appear to be available"),
            timeout: TimeSpan.FromSeconds(5));

        // The app must still be alive and responsive, not crashed -- a
        // second interaction (Refresh) should work without throwing.
        Assert.False(testApp.App.HasExited);
        var refreshButton = testApp.MainWindow.FindFirstDescendant(cf => cf.ByAutomationId(AutomationIds.RefreshButton))!.AsButton();
        refreshButton.Invoke();
        Assert.False(testApp.App.HasExited);
    }

    [Fact]
    public void MissingRegistryFile_ShowsErrorDialog_InsteadOfCrashing()
    {
        var missingPath = Path.Combine(Path.GetTempPath(), $"does-not-exist-{Guid.NewGuid():N}.json");

        using var testApp = UiTestApp.Launch(new Dictionary<string, string>
        {
            ["VERSION_SELECTOR_REGISTRY"] = missingPath,
        });

        Assert.Contains("Registry Error", testApp.MainWindow.Title);

        var okButton = testApp.MainWindow.FindFirstDescendant(cf => cf.ByControlType(ControlType.Button))?.AsButton();
        okButton?.Invoke();
    }
}
