namespace VersionSelector.Tests;

internal static class TestPaths
{
    /// <summary>Locates the compiled VersionSelector.exe next to this test
    /// assembly's sibling build output. VERSION_SELECTOR_EXE_PATH overrides
    /// this (e.g. for a CI job building Release), otherwise this walks the
    /// conventional sibling-project bin layout, matching whatever
    /// configuration/TFM this test assembly itself was built with.</summary>
    public static string FindVersionSelectorExe()
    {
        var overridePath = Environment.GetEnvironmentVariable("VERSION_SELECTOR_EXE_PATH");
        if (!string.IsNullOrEmpty(overridePath))
        {
            if (!File.Exists(overridePath))
            {
                throw new FileNotFoundException(
                    $"VERSION_SELECTOR_EXE_PATH was set but no file exists there: {overridePath}");
            }
            return overridePath;
        }

#if DEBUG
        const string configuration = "Debug";
#else
        const string configuration = "Release";
#endif
        var targetFramework = System.Runtime.InteropServices.RuntimeInformation
            .FrameworkDescription.Contains("8.")
            ? "net8.0-windows"
            : "net8.0-windows";

        // Tests build to .../VersionSelector.Tests/bin/<Configuration>/net8.0-windows/
        // The app builds to  .../VersionSelector/bin/<Configuration>/net8.0-windows/VersionSelector.exe
        var candidate = Path.GetFullPath(Path.Combine(
            AppContext.BaseDirectory, "..", "..", "..", "..",
            "VersionSelector", "bin", configuration, targetFramework, "VersionSelector.exe"));

        if (!File.Exists(candidate))
        {
            throw new FileNotFoundException(
                "Could not find VersionSelector.exe. Build the VersionSelector project first " +
                "(dotnet build tools/version-selector/VersionSelector.sln), or set " +
                $"VERSION_SELECTOR_EXE_PATH explicitly. Looked for: {candidate}");
        }

        return candidate;
    }
}
