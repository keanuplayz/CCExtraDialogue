using DialogueEditor.Models;
using System;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace DialogueEditor.Modules
{
    interface ICharacterExpressionsProvider
    {
        event EventHandler Loaded;

        IReadOnlyList<CharacterExpression> CharacterExpressions { get; }

        Task<bool> LoadFrom(string directory);
    }
}
