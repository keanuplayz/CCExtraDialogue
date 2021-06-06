using DialogueEditor.Models;
using System;
using System.Windows;
using System.Windows.Controls;

namespace DialogueEditor.Controls
{
    /// <summary>
    /// Interaction logic for ExpressionsList.xaml
    /// </summary>
    public partial class GridOptionsList : UserControl
    {
        public event EventHandler<Option> OptionClick;

        public GridOptionsList()
        {
            InitializeComponent();
        }

        private void Option_Click(object sender, RoutedEventArgs e)
        {
            var selectedOption = (sender as Control)?.DataContext as Option;
            
            if (selectedOption != null)
                OptionClick?.Invoke(sender, selectedOption);
        }
    }
}
