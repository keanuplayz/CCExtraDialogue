using DialogueEditor.Models;
using DialogueEditor.Utils;
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Threading.Tasks;

namespace DialogueEditor.Modules
{
    class CharacterExpressionsProvider : ICharacterExpressionsProvider
    {
        public event EventHandler Loaded;

        List<CharacterExpression> _characterExpressions = new List<CharacterExpression>();

        public IReadOnlyList<CharacterExpression> CharacterExpressions { get { return _characterExpressions.AsReadOnly(); } }

        public async Task<bool> LoadFrom(string directory)
        {
            try
            {
                var loadedCharacterExpressions = new List<CharacterExpression>();
                var characterDirectories = Directory.GetDirectories(directory);

                object loadingLock = new object();

                var loadingTasks = new List<Task<List<CharacterExpression>>>();

                foreach (var characterDirectory in characterDirectories)
                {
                    var task = LoadCharacterExpressions(characterDirectory);
                    loadingTasks.Add(task);
                    task.Start();
                }

                await Task.WhenAll(loadingTasks);

                foreach (var task in loadingTasks)
                    loadedCharacterExpressions.AddRange(task.Result);

                _characterExpressions = loadedCharacterExpressions;
                Loaded?.Invoke(this, EventArgs.Empty);
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"{nameof(CharacterExpressionsProvider)} - {ex.Message}");
                return false;
            }

            return true;
        }

        Task<List<CharacterExpression>> LoadCharacterExpressions(string characterDirectoryPath)
        {
            return new Task<List<CharacterExpression>>(() =>
            {
                var characterExpressions = new List<CharacterExpression>();
                var characterName = Path.GetFileNameWithoutExtension(characterDirectoryPath);
                var expressionFiles = Directory.GetFiles(characterDirectoryPath);
                foreach (var expressionFile in expressionFiles)
                {
                    var expressionName = Path.GetFileNameWithoutExtension(expressionFile);
                    var expressionBitmap = BitmapHelper.CreateBitmapFromFile(expressionFile);
                    characterExpressions.Add(new CharacterExpression(characterName, expressionName, expressionBitmap));
                }

                return characterExpressions;
            });
        }
    }
}
