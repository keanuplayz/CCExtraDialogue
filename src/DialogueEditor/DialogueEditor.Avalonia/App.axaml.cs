using Avalonia;
using Avalonia.Controls;
using Avalonia.Controls.ApplicationLifetimes;
using Avalonia.Markup.Xaml;
using DialogueEditor.Avalonia.Modules;
using DialogueEditor.Avalonia.ViewModels;
using DialogueEditor.Avalonia.Views;
using DialogueEditor.Models;
using System.IO;
using System.Linq;

namespace DialogueEditor.Avalonia
{
    public class App : Application
    {
        public override void Initialize()
        {
            AvaloniaXamlLoader.Load(this);
        }

        public override async void OnFrameworkInitializationCompleted()
        {
            if (ApplicationLifetime is IClassicDesktopStyleApplicationLifetime desktop)
            {

                string expressionsDirPath = Directory.GetCurrentDirectory();

                // Load character expressions into memory
                var expressionsProvider = new CharacterExpressionsProvider();
                var loadResult = await expressionsProvider.LoadFrom(expressionsDirPath);

                if (loadResult != true)
                {
                    desktop.Shutdown();
                    return;
                }

                var optionsList = expressionsProvider.CharacterExpressions.Select(ce => new Option(ce, ce.Expression, ce.Image));

                if (optionsList.Count() == 0)
                {
                    desktop.Shutdown();
                    return;
                }

                var vm = new MainViewModel(optionsList);
                desktop.MainWindow = new MainView()
                {
                    DataContext = vm,
                };
                desktop.MainWindow.Show();
                desktop.MainWindow.Activate();
            }

            base.OnFrameworkInitializationCompleted();
        }
    }
}
