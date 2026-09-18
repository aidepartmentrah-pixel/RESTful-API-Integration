namespace VersionSelector;

/// <summary>One entry in the local version registry (see VersionRegistry).</summary>
public sealed class VersionEntry
{
    public required string Name { get; init; }
    public required string ComposeProject { get; init; }
    public required string WorkingDirectory { get; init; }
    public required int Port { get; init; }
}
