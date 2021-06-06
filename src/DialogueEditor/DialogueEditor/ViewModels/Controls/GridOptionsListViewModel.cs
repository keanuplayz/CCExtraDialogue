using DialogueEditor.Models;
using MvvmExtensions.PropertyChangedMonitoring;
using System.Collections.Generic;

namespace DialogueEditor.ViewModels.Controls
{
    public class GridOptionsListViewModel : PropertyChangedImplementation
    {
        public IEnumerable<Option> Options { get; }

        public GridOptionsListViewModel(IEnumerable<Option> options)
        {
            Options = options;
        }
    }
}
