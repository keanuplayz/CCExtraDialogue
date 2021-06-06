using DialogueEditor.Models;
using MvvmExtensions.Attributes;
using MvvmExtensions.Commands;
using MvvmExtensions.PropertyChangedMonitoring;
using System.Collections.Generic;
using System.Linq;
using System.Windows.Input;

namespace DialogueEditor
{
    public class MainViewModel : PropertyChangedImplementation
    {
        List<Option> _options = new List<Option>();

        string _characterFilter = string.Empty;
        string _expressionFilter = string.Empty;
        Dictionary<string, List<Option>> _characterExpressionOptionsDictionary = new Dictionary<string, List<Option>>();

        public List<string> CharactersList { get; } = new List<string>();

        public string CharacterFilter 
        {
            get { return _characterFilter; }
            set { Set(ref _characterFilter, value); }
        }

        public string ExpressionFilter
        {
            get { return _expressionFilter; }
            set { Set(ref _expressionFilter, value); }
        }

        [DependsOn(nameof(CharacterFilter), nameof(ExpressionFilter))]
        public List<Option> FilteredOptionsList 
        { 
            get
            {
                return GetFilteredOptionsList();
            }
        }

        public ICommand OpenNewWindowCommand
        {
            get
            {
                return new DelegateCommand
                {
                    CommandAction = (x) =>
                    {
                        OpenNewWindow();
                    }
                };
            }
        }

        public MainViewModel(IEnumerable<Option> options, string defaultCharacterFilter = null, string defaultExpressionFilter = null)
        {
            _options.AddRange(options);

            var characters = _options.Select(o => (o.OptionData as CharacterExpression).Character).Distinct();
            
            CharactersList.AddRange(characters);
            foreach (var character in CharactersList)
            {
                var characterExpressions = _options.Where(o => (o.OptionData as CharacterExpression).Character == character);
                _characterExpressionOptionsDictionary[character] = new List<Option>(characterExpressions);
            }

            CharacterFilter = defaultCharacterFilter ?? CharactersList.First();
            ExpressionFilter = defaultExpressionFilter ?? string.Empty;
        }

        List<Option> GetFilteredOptionsList()
        {
            return _characterExpressionOptionsDictionary[CharacterFilter]
                .Where(o => (o.OptionData as CharacterExpression).Expression.ToLowerInvariant().Contains(ExpressionFilter.ToLowerInvariant()))
                .ToList();
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

        void OpenNewWindow()
        {
            var optionsListCopy = new List<Option>(_options);
            var vm = new MainViewModel(optionsListCopy, CharacterFilter, ExpressionFilter);
            var newWindow = new MainView(vm);
            newWindow.ShowActivated = false; // Lack of activation allows to quickly open multiple windows without loosing focus
            newWindow.Show();
        }
    }
}