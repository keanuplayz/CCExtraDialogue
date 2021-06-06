using DialogueEditor.Models;
using DialogueEditor.Modules;
using Ookii.Dialogs.Wpf;
using System;
using System.Linq;
using System.Windows;

namespace DialogueEditor
{
    /// <summary>
    /// Interaction logic for App.xaml
    /// </summary>
    public partial class App : Application
    {
        protected override async void OnStartup(StartupEventArgs e)
        {
            base.OnStartup(e);

            // Show directory selection dialog and get path from user
            VistaFolderBrowserDialog fbd = new VistaFolderBrowserDialog();
            fbd.SelectedPath = AppDomain.CurrentDomain.BaseDirectory;
            fbd.UseDescriptionForTitle = true;
            fbd.Description = "Select parent directory of directories with compiled expressions";
            var openDirResult = fbd.ShowDialog();

            if (openDirResult != true)
            {
                Shutdown();
                return;
            }

            // Load character expressions into memory
            var expressionsProvider = new CharacterExpressionsProvider();
            var loadResult = await expressionsProvider.LoadFrom(fbd.SelectedPath);

            if (loadResult != true)
            {
                MessageBox.Show("An error occured during expressions loading.");
                Shutdown();
                return;
            }

            var optionsList = expressionsProvider.CharacterExpressions.Select(ce => new Option(ce, ce.Expression, ce.Image));

            if (optionsList.Count() == 0)
            {
                MessageBox.Show($"Loaded 0 expressions from \"{fbd.SelectedPath}\"" 
                    + Environment.NewLine + "Click OK to close application.");
                Shutdown();
                return;
            }

            // Initialize and display main window
            var vm = new MainViewModel(optionsList);
            var view = new MainView(vm);
            view.Show();
            view.Activate();
        }
    }
}
