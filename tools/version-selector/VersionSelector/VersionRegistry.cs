using System.Text.Json;

namespace VersionSelector;

public sealed class VersionRegistryLoadException : Exception
{
    public VersionRegistryLoadException(string message, Exception? inner = null) : base(message, inner) { }
}

/// <summary>
/// Reads the local, gitignored JSON registry of API versions this tool can
/// start/stop/restart. See tools/version-selector/local.versions.json.example
/// for the expected shape.
/// </summary>
public static class VersionRegistry
{
    private sealed class RegistryFile
    {
        public List<VersionEntryDto>? Versions { get; set; }
    }

    private sealed class VersionEntryDto
    {
        public string? Name { get; set; }
        public string? ComposeProject { get; set; }
        public string? WorkingDirectory { get; set; }
        public int? Port { get; set; }
    }

    private static readonly JsonSerializerOptions Options = new()
    {
        PropertyNameCaseInsensitive = true,
    };

    public static IReadOnlyList<VersionEntry> Load(string path)
    {
        if (!File.Exists(path))
        {
            throw new VersionRegistryLoadException(
                $"Registry file not found: {path}\n\n" +
                "Copy tools/version-selector/local.versions.json.example to that " +
                "path and fill in your own worktree directories/ports.");
        }

        string json;
        try
        {
            json = File.ReadAllText(path);
        }
        catch (IOException ex)
        {
            throw new VersionRegistryLoadException($"Could not read registry file: {path}", ex);
        }

        RegistryFile? parsed;
        try
        {
            parsed = JsonSerializer.Deserialize<RegistryFile>(json, Options);
        }
        catch (JsonException ex)
        {
            throw new VersionRegistryLoadException($"Registry file is not valid JSON: {path}", ex);
        }

        if (parsed?.Versions is null || parsed.Versions.Count == 0)
        {
            throw new VersionRegistryLoadException(
                $"Registry file has no \"versions\" entries: {path}");
        }

        var result = new List<VersionEntry>(parsed.Versions.Count);
        for (var i = 0; i < parsed.Versions.Count; i++)
        {
            var dto = parsed.Versions[i];
            var missing = new List<string>();
            if (string.IsNullOrWhiteSpace(dto.Name)) missing.Add("name");
            if (string.IsNullOrWhiteSpace(dto.ComposeProject)) missing.Add("composeProject");
            if (string.IsNullOrWhiteSpace(dto.WorkingDirectory)) missing.Add("workingDirectory");
            if (dto.Port is null) missing.Add("port");

            if (missing.Count > 0)
            {
                throw new VersionRegistryLoadException(
                    $"versions[{i}] is missing required field(s): {string.Join(", ", missing)}");
            }

            result.Add(new VersionEntry
            {
                Name = dto.Name!,
                ComposeProject = dto.ComposeProject!,
                WorkingDirectory = dto.WorkingDirectory!,
                Port = dto.Port!.Value,
            });
        }

        return result;
    }
}
