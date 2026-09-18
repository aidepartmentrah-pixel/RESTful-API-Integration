namespace VersionSelector;

internal static class Program
{
    [STAThread]
    private static void Main()
    {
        Application.SetHighDpiMode(HighDpiMode.SystemAware);
        Application.EnableVisualStyles();
        Application.SetCompatibleTextRenderingDefault(false);

        var registryPath = Environment.GetEnvironmentVariable("VERSION_SELECTOR_REGISTRY")
            ?? FindDefaultRegistryPath();

        var dockerRunner = CreateDockerRunner();

        IReadOnlyList<VersionEntry> versions;
        try
        {
            versions = VersionRegistry.Load(registryPath);
        }
        catch (VersionRegistryLoadException ex)
        {
            MessageBox.Show(ex.Message, "Version Selector - Registry Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            return;
        }

        Application.Run(new MainForm(versions, dockerRunner));
    }

    /// <summary>Test mode: when VERSION_SELECTOR_FAKE_DOCKER_STATE is set,
    /// the compiled EXE runs against an in-memory fake instead of real
    /// Docker -- see FakeDockerRunner's doc comment. Used only by the fast
    /// FlaUI suite; never set in normal use.</summary>
    private static IDockerRunner CreateDockerRunner()
    {
        var fakeStatePath = Environment.GetEnvironmentVariable("VERSION_SELECTOR_FAKE_DOCKER_STATE");
        if (string.IsNullOrEmpty(fakeStatePath))
        {
            return new RealDockerRunner();
        }

        var logPath = Environment.GetEnvironmentVariable("VERSION_SELECTOR_FAKE_DOCKER_LOG");
        return FakeDockerRunner.LoadFromStateFile(fakeStatePath, logPath);
    }

    /// <summary>Walks up from the EXE's own directory looking for
    /// local.versions.json, stopping at the repo root (.git folder) if not
    /// found sooner. Returns the expected path even if the file doesn't
    /// exist yet -- VersionRegistry.Load gives a clear error in that case.</summary>
    private static string FindDefaultRegistryPath()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null)
        {
            var candidate = Path.Combine(dir.FullName, "local.versions.json");
            if (File.Exists(candidate))
            {
                return candidate;
            }
            if (Directory.Exists(Path.Combine(dir.FullName, ".git")))
            {
                return candidate;
            }
            dir = dir.Parent;
        }
        return Path.Combine(AppContext.BaseDirectory, "local.versions.json");
    }
}
