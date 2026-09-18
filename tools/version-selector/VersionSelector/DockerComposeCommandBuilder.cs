namespace VersionSelector;

public enum DockerAction
{
    Up,
    Down,
    Restart,
}

/// <summary>Pure command-construction logic, kept separate from process
/// launching so it's directly unit-testable without touching Docker.</summary>
public static class DockerComposeCommandBuilder
{
    public static string BuildArguments(string composeProject, DockerAction action)
    {
        var verb = action switch
        {
            DockerAction.Up => "up -d",
            DockerAction.Down => "down",
            DockerAction.Restart => "restart",
            _ => throw new ArgumentOutOfRangeException(nameof(action)),
        };
        return $"compose -p {composeProject} {verb}";
    }

    public static string BuildPsArguments(string composeProject)
    {
        return $"ps --filter \"label=com.docker.compose.project={composeProject}\" --format \"{{{{.Names}}}}\t{{{{.State}}}}\"";
    }
}
