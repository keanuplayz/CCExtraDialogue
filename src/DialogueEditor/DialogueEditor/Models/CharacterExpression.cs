using System;
using System.Windows.Media.Imaging;

namespace DialogueEditor.Models
{
    class CharacterExpression
    {
        public string Id { get { return $"{Character}-{Expression}"; } }

        public string Character { get; }
        
        public string Expression { get; }

        public BitmapImage Image { get; }

        public CharacterExpression(string character, string expression, BitmapImage image)
        {
            Character = character ?? throw new ArgumentNullException(nameof(character));
            Expression = expression ?? throw new ArgumentNullException(nameof(expression));
            Image = image;
        }
    }
}
