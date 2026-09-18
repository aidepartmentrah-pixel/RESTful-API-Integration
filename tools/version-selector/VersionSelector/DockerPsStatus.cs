namespace VersionSelector;

public enum DockerPsStatus
{
    Unknown,
    Stopped,
    Starting,
    Running,
    Unavailable,
}

/// <summary>Pure parsing logic for `docker ps` output, kept separate from
/// process launching so it's directly unit-testable.</summary>
public static class DockerPsParser
{
    /// <param name="output">Tab-separated "Name\tState" lines, one container
    /// per line -- the shape produced by
    /// DockerComposeCommandBuilder.BuildPsArguments's --format.</param>
    public static DockerPsStatus Parse(string output)
    {
        var lines = output
            .Split('\n', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries)
            .ToList();

        if (lines.Count == 0)
        {
            return DockerPsStatus.Stopped;
        }

        var states = lines
            .Select(line => line.Split('\t'))
            .Where(parts => parts.Length >= 2)
            .Select(parts => parts[1].Trim().ToLowerInvariant())
            .ToList();

        if (states.Count == 0)
        {
            return DockerPsStatus.Stopped;
        }

        if (states.All(s => s == "running"))
        {
            return DockerPsStatus.Running;
        }

        if (states.Any(s => s is "running" or "restarting" or "created"))
        {
            return DockerPsStatus.Starting;
        }

        return DockerPsStatus.Stopped;
    }
}
