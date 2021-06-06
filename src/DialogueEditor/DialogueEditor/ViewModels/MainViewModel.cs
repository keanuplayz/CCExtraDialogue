using DialogueEditor.Models;
using MvvmExtensions.PropertyChangedMonitoring;
using System.Collections.Generic;


namespace DialogueEditor
{
    public class MainViewModel : PropertyChangedImplementation
    {
        public List<Option> OptionsList { get; } = new List<Option>();

        public MainViewModel(IEnumerable<Option> options)
        {
            OptionsList.AddRange(options);
        }

        internal void OnOptionSelected(Option option)
        {
            var expression = (option.OptionData as CharacterExpression);
            if (expression != null)
            {
                var copiedText = $"{expression.Character} > {expression.Expression} ";
                System.Windows.Clipboard.SetText(copiedText);
            }
        }
    }
}