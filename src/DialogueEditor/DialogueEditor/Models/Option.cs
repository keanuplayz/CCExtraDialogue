using System.Windows.Media.Imaging;

namespace DialogueEditor.Models
{
    public class Option
    {
        // Todo: Refactor options to stoge generic <T> data instead of objet
        public object OptionData { get; }

        public string Title { get; }

        public BitmapImage Image { get; }

        public Option(object optionData, string title, BitmapImage image)
        {
            OptionData = optionData;
            Title = title;
            Image = image;
        }
    }
}
