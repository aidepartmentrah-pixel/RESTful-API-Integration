namespace VersionSelector;

public sealed class DockerCommandResult
{
    public required bool Success { get; init; }
    public required bool DockerUnavailable { get; init; }
    public string StandardOutput { get; init; } = "";
    public string StandardError { get; init; } = "";
}

/// <summary>
/// Boundary between the UI and the actual `docker` process. Kept as an
/// interface so the fast FlaUI test suite can swap in FakeDockerRunner
/// (via Program.cs's test-mode env vars) and never touch real Docker.
/// </summary>
public interface IDockerRunner
{
    DockerCommandResult RunCompose(string workingDirectory, string composeProject, DockerAction action);
    DockerPsStatus GetStatus(string composeProject);
}
