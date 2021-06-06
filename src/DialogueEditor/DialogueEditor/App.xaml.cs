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

            var tskd = new TaskDialog();
            tskd.MainInstruction = "This app requires a directory with compiled expressions like this:"
                + Environment.NewLine
                + Environment.NewLine
                + "directory/character1/expression1.img"
                + Environment.NewLine
                + "directory/character1/expression1.img"
                + Environment.NewLine
                + "directory/character2/expression2.img"
                + Environment.NewLine
                + "directory/character2/expression2.img"
                + Environment.NewLine
                + Environment.NewLine
                + "etc...";

            var manualBtn = new TaskDialogButton("Pick Directory");
            var currentBtn = new TaskDialogButton("Use Current");
            var cancelBtn = new TaskDialogButton(ButtonType.Cancel);

            tskd.Buttons.Add(currentBtn);
            tskd.Buttons.Add(manualBtn);
            tskd.Buttons.Add(cancelBtn);

            var result = tskd.ShowDialog();

            if (result == cancelBtn)
            {
                Shutdown();
                return;
            }

            string expressionsDirPath = AppDomain.CurrentDomain.BaseDirectory;
            if (result == manualBtn)
            {
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

                expressionsDirPath = fbd.SelectedPath;
            }

            // Load character expressions into memory
            var expressionsProvider = new CharacterExpressionsProvider();
            var loadResult = await expressionsProvider.LoadFrom(expressionsDirPath);

            if (loadResult != true)
            {
                MessageBox.Show("An error occured during expressions loading.");
                Shutdown();
                return;
            }

            var optionsList = expressionsProvider.CharacterExpressions.Select(ce => new Option(ce, ce.Expression, ce.Image));

            if (optionsList.Count() == 0)
            {
                MessageBox.Show($"Loaded 0 expressions from \"{expressionsDirPath}\"" 
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
