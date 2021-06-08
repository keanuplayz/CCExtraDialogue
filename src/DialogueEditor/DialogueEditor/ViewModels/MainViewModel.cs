using DialogueEditor.Models;
using MvvmExtensions.Attributes;
using MvvmExtensions.Commands;
using MvvmExtensions.PropertyChangedMonitoring;
using System;
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
        bool _showStatic = true;
        bool _showAnimations = true;

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

        public bool ShowStatic
        {
            get { return _showStatic; }
            set { Set(ref _showStatic, value); }
        }

        public bool ShowAnimations
        {
            get { return _showAnimations; }
            set { Set(ref _showAnimations, value); }
        }

        [DependsOn(nameof(CharacterFilter), nameof(ExpressionFilter), nameof(ShowStatic), nameof(ShowAnimations))]
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

        public MainViewModel(IEnumerable<Option> options)
        {
            _options.AddRange(options);

            var characters = _options.Select(o => (o.OptionData as CharacterExpression).Character).Distinct();
            
            CharactersList.AddRange(characters);
            foreach (var character in CharactersList)
            {
                var characterExpressions = _options.Where(o => (o.OptionData as CharacterExpression).Character == character);
                _characterExpressionOptionsDictionary[character] = new List<Option>(characterExpressions);
            }

            var lea = CharactersList.FirstOrDefault((c) => string.Equals(c, "lea", StringComparison.OrdinalIgnoreCase));
            CharacterFilter = lea ?? CharactersList.First();
        }

        List<Option> GetFilteredOptionsList()
        {
            return _characterExpressionOptionsDictionary[CharacterFilter]
                .Where(o => (o.OptionData as CharacterExpression).Expression.LastIndexOf(' ') > 0
                && char.IsDigit((o.OptionData as CharacterExpression).Expression.Last()) ? ShowAnimations : ShowStatic)
                .Where(o => (o.OptionData as CharacterExpression).Expression.ToLowerInvariant().Contains(ExpressionFilter.ToLowerInvariant()))
                .ToList();
        }

        internal void OnOptionSelected(Option option)
        {
            var expression = (option.OptionData as CharacterExpression);
            if (expression != null)
            {
                var copiedText = $"{expression.Character} > {expression.Expression} ";

                // Remote index if its a frame from animation
                if (copiedText.LastIndexOf(' ') > 0 && char.IsDigit(copiedText.Last()))
                    copiedText.Substring(0, copiedText.LastIndexOf(' '));

                System.Windows.Clipboard.SetText(copiedText);
            }
        }

        void OpenNewWindow()
        {
            var optionsListCopy = new List<Option>(_options);
            var vm = new MainViewModel(optionsListCopy)
            {
                // Copy current filtering settings
                CharacterFilter = CharacterFilter,
                ExpressionFilter = ExpressionFilter,
                ShowStatic = ShowStatic,
                ShowAnimations = ShowAnimations,
            };
            var newWindow = new MainView(vm);
            newWindow.ShowActivated = false; // Lack of activation allows to quickly open multiple windows without loosing focus
            newWindow.Show();
        }
    }
}