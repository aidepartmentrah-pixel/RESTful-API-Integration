using FlaUI.Core.AutomationElements;
using FlaUI.Core.Definitions;

namespace VersionSelector.Tests;

internal static class AutomationElementExtensions
{
    /// <summary>Row text for a WinForms ListView in Details view, as FlaUI's
    /// UIA3 provider exposes it: ListItem children each with N Text
    /// children (one per column, AutomationId "ListViewSubItem-{n}").</summary>
    public static List<string[]> GetListViewRows(this AutomationElement listView)
    {
        var rows = listView.FindAllChildren(cf => cf.ByControlType(ControlType.ListItem));
        return rows
            .Select(row => row
                .FindAllChildren(cf => cf.ByControlType(ControlType.Text))
                .Select(cell => cell.Name)
                .ToArray())
            .ToList();
    }

    /// <summary>Selects a ListView row via the UIA SelectionItem pattern --
    /// more reliable for automation than simulating a physical mouse click,
    /// which depends on accurate screen coordinates and window focus.</summary>
    public static void SelectListViewRow(this AutomationElement listView, int index)
    {
        var row = listView.FindAllChildren(cf => cf.ByControlType(ControlType.ListItem))[index];
        row.Patterns.SelectionItem.Pattern.Select();
    }
}
