using VersionSelector;
using Xunit;

namespace VersionSelector.Tests;

public class VersionRegistryTests
{
    [Fact]
    public void Load_ValidFile_ReturnsAllEntries()
    {
        var path = Path.Combine(AppContext.BaseDirectory, "Fixtures", "test-registry.json");
        var versions = VersionRegistry.Load(path);

        Assert.Equal(2, versions.Count);
        Assert.Equal("v1.1 (stable)", versions[0].Name);
        Assert.Equal("mock-v11", versions[0].ComposeProject);
        Assert.Equal(6000, versions[0].Port);
        Assert.Equal("v1.2-dev", versions[1].Name);
        Assert.Equal(6001, versions[1].Port);
    }

    [Fact]
    public void Load_MissingFile_ThrowsWithHelpfulMessage()
    {
        var path = Path.Combine(AppContext.BaseDirectory, "Fixtures", "does-not-exist.json");
        var ex = Assert.Throws<VersionRegistryLoadException>(() => VersionRegistry.Load(path));
        Assert.Contains("not found", ex.Message, StringComparison.OrdinalIgnoreCase);
    }

    [Fact]
    public void Load_MalformedJson_ThrowsWithHelpfulMessage()
    {
        var path = Path.Combine(AppContext.BaseDirectory, "Fixtures", "malformed-registry.json");
        var ex = Assert.Throws<VersionRegistryLoadException>(() => VersionRegistry.Load(path));
        Assert.Contains("not valid JSON", ex.Message, StringComparison.OrdinalIgnoreCase);
    }

    [Fact]
    public void Load_EmptyVersionsList_Throws()
    {
        var path = Path.Combine(AppContext.BaseDirectory, "Fixtures", "empty-registry.json");
        var ex = Assert.Throws<VersionRegistryLoadException>(() => VersionRegistry.Load(path));
        Assert.Contains("no", ex.Message, StringComparison.OrdinalIgnoreCase);
    }

    [Fact]
    public void Load_MissingRequiredField_ThrowsNamingIt()
    {
        var path = Path.Combine(AppContext.BaseDirectory, "Fixtures", "missing-field-registry.json");
        var ex = Assert.Throws<VersionRegistryLoadException>(() => VersionRegistry.Load(path));
        Assert.Contains("port", ex.Message, StringComparison.OrdinalIgnoreCase);
    }
}
