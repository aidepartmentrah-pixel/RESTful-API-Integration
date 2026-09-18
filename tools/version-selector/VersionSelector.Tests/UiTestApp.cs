using System.Diagnostics;
using FlaUI.Core;
using FlaUI.Core.AutomationElements;
using FlaUI.UIA3;

namespace VersionSelector.Tests;

/// <summary>Launches the compiled VersionSelector.exe under test, wiring up
/// whatever env vars the caller needs (fake docker state/log, registry
/// override), and disposes both the automation session and the process on
/// Dispose.</summary>
public sealed class UiTestApp : IDisposable
{
    public Application App { get; }
    public UIA3Automation Automation { get; }
    public Window MainWindow { get; }

    private UiTestApp(Application app, UIA3Automation automation, Window mainWindow)
    {
        App = app;
        Automation = automation;
        MainWindow = mainWindow;
    }

    public static UiTestApp Launch(IDictionary<string, string> environmentVariables)
    {
        var exePath = TestPaths.FindVersionSelectorExe();

        var startInfo = new ProcessStartInfo
        {
            FileName = exePath,
            UseShellExecute = false,
        };
        foreach (var (key, value) in environmentVariables)
        {
            startInfo.Environment[key] = value;
        }

        var app = Application.Launch(startInfo);
        var automation = new UIA3Automation();
        var window = app.GetMainWindow(automation, TimeSpan.FromSeconds(15))
            ?? throw new InvalidOperationException("VersionSelector.exe did not show a main window in time.");

        return new UiTestApp(app, automation, window);
    }

    public void Dispose()
    {
        try
        {
            if (!App.HasExited)
            {
                App.Close();
            }
        }
        catch
        {
            // best effort
        }
        Automation.Dispose();
        App.Dispose();
    }
}
