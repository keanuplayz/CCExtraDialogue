using DialogueEditor.Models;
using MahApps.Metro.Controls;

namespace DialogueEditor
{
    /// <summary>
    /// Interaction logic for MainWindow.xaml
    /// </summary>
    public partial class MainView : MetroWindow
    {
        public MainView(MainViewModel vm)
        {
            InitializeComponent();
            DataContext = vm;
        }

        private void GridOptionsList_OptionClick(object sender, Option option)
        {
            (DataContext as MainViewModel)?.OnOptionSelected(option);
        }
    }
}
