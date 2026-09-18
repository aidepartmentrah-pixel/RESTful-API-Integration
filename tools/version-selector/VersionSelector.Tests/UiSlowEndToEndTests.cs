using System.Net.Http;
using FlaUI.Core.AutomationElements;
using Xunit;

namespace VersionSelector.Tests;

/// <summary>
/// The one true end-to-end test: drives the real compiled EXE (real
/// RealDockerRunner, no fake env vars) against the real mock-v11 worktree
/// set up in Period A (../RESTful-API-Integration-v1.1, compose project
/// "mock-v11", port 6000). Requires Docker Desktop running and that
/// worktree present -- this is NOT part of the fast suite; run explicitly
/// with `dotnet test --filter Category=Slow`.
///
/// Leaves mock-v11 running when it finishes (its state before this test
/// started, per this repo's normal working setup), whichever way the test
/// exits.
/// </summary>
[Collection("UI Tests")]
[Trait("Category", "Slow")]
public class UiSlowEndToEndTests
{
    private const string ComposeProject = "mock-v11";
    private const int Port = 6000;
    private static readonly HttpClient Http = new() { Timeout = TimeSpan.FromSeconds(3) };

    private static string FindRepoRoot()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null)
        {
            if (Directory.Exists(Path.Combine(dir.FullName, ".git")))
            {
                return dir.FullName;
            }
            dir = dir.Parent;
        }
        throw new InvalidOperationException("Could not find repo root (.git) above " + AppContext.BaseDirectory);
    }

    private static string WriteRealRegistryFixture()
    {
        var repoRoot = FindRepoRoot();
        var v11WorktreePath = Path.GetFullPath(Path.Combine(repoRoot, "..", "RESTful-API-Integration-v1.1"));

        if (!Directory.Exists(v11WorktreePath))
        {
            throw new SkipException(
                $"v1.1 worktree not found at {v11WorktreePath} -- set up Period A's " +
                "`git worktree add ../RESTful-API-Integration-v1.1 v1.1.0` first.");
        }

        var json = $$"""
            {
              "versions": [
                {
                  "name": "v1.1 (stable)",
                  "composeProject": "{{ComposeProject}}",
                  "workingDirectory": "{{v11WorktreePath.Replace("\\", "\\\\")}}",
                  "port": {{Port}}
                }
              ]
            }
            """;

        var path = Path.Combine(Path.GetTempPath(), $"version-selector-real-registry-{Guid.NewGuid():N}.json");
        File.WriteAllText(path, json);
        return path;
    }

    private static async Task<bool> IsHealthy()
    {
        try
        {
            var response = await Http.GetAsync($"http://localhost:{Port}/api/directory/v1/health");
            return response.IsSuccessStatusCode;
        }
        catch
        {
            return false;
        }
    }

    private static async Task<bool> PollUntilAsync(Func<Task<bool>> condition, TimeSpan timeout, TimeSpan interval)
    {
        var deadline = DateTime.UtcNow + timeout;
        while (DateTime.UtcNow < deadline)
        {
            if (await condition())
            {
                return true;
            }
            await Task.Delay(interval);
        }
        return await condition();
    }

    [SkippableFact]
    public async Task StartAndStop_ThroughRealUi_ActuallyControlsThePort()
    {
        var registryPath = WriteRealRegistryFixture();

        using var testApp = UiTestApp.Launch(new Dictionary<string, string>
        {
            ["VERSION_SELECTOR_REGISTRY"] = registryPath,
        });

        var listView = testApp.MainWindow.FindFirstDescendant(cf => cf.ByAutomationId(AutomationIds.VersionsListView))!;
        listView.SelectListViewRow(0);

        var stopButton = testApp.MainWindow.FindFirstDescendant(cf => cf.ByAutomationId(AutomationIds.StopButton))!.AsButton();
        var startButton = testApp.MainWindow.FindFirstDescendant(cf => cf.ByAutomationId(AutomationIds.StartButton))!.AsButton();

        try
        {
            // Stop -> port must stop responding.
            stopButton.Invoke();
            var stopped = await PollUntilAsync(async () => !await IsHealthy(),
                timeout: TimeSpan.FromSeconds(60), interval: TimeSpan.FromSeconds(2));
            Assert.True(stopped, "Port 6000 kept responding after Stop was clicked through the UI.");

            // Start -> port must respond again.
            startButton.Invoke();
            var started = await PollUntilAsync(async () => await IsHealthy(),
                timeout: TimeSpan.FromSeconds(90), interval: TimeSpan.FromSeconds(2));
            Assert.True(started, "Port 6000 never came back up after Start was clicked through the UI.");
        }
        finally
        {
            // Best-effort: leave mock-v11 running, matching this repo's
            // normal working state, regardless of pass/fail above.
            if (!await IsHealthy())
            {
                startButton.Invoke();
                await PollUntilAsync(async () => await IsHealthy(),
                    timeout: TimeSpan.FromSeconds(90), interval: TimeSpan.FromSeconds(2));
            }
            File.Delete(registryPath);
        }
    }
}
