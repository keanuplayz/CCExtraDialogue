using Avalonia.Media.Imaging;

namespace DialogueEditor.Avalonia.Utils
{
    static class BitmapHelper
    {
        public static IBitmap TrimTransparentSpace(this IBitmap bitmap)
        {
            // Todo: Implement transparency crop

            return bitmap;
        }

        public static IBitmap CreateBitmapFromFile(string filePath)
        {
            return new Bitmap(filePath);
        }
    }
}
