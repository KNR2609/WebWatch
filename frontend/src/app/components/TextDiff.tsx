interface TextDiffProps {
  oldText: string;
  newText: string;
  label: string;
}

export function TextDiff({ oldText, newText, label }: TextDiffProps) {
  // Simple word-level diff highlighting
  const oldWords = oldText.split(/(\s+)/);
  const newWords = newText.split(/(\s+)/);

  const renderDiff = (words: string[], isBaseline: boolean) => {
    const comparisonWords = isBaseline ? newWords : oldWords;
    const comparisonText = isBaseline ? newText : oldText;

    return words.map((word, index) => {
      if (/^\s+$/.test(word)) {
        return <span key={index}>{word}</span>;
      }

      const isInComparison = comparisonText.includes(word);
      const isDifferent = !isInComparison || word !== comparisonWords[index];

      if (isDifferent && word.trim()) {
        return (
          <span
            key={index}
            className={`${
              isBaseline
                ? 'bg-red-100 text-red-900 border-b-2 border-red-400'
                : 'bg-green-100 text-green-900 border-b-2 border-green-400'
            } px-0.5 font-medium`}
          >
            {word}
          </span>
        );
      }

      return <span key={index}>{word}</span>;
    });
  };

  return (
    <div className="space-y-4">
      <div>
        <div className="mb-2">
          <span className="inline-block px-3 py-1.5 text-xs font-medium bg-red-50 text-red-700 border border-red-200 rounded-md">
            Baseline (Yesterday) - {label}
          </span>
        </div>
        <div className="p-4 bg-red-50 border-2 border-red-200 rounded-lg text-sm leading-relaxed text-gray-800">
          {renderDiff(oldWords, true)}
        </div>
      </div>

      <div>
        <div className="mb-2">
          <span className="inline-block px-3 py-1.5 text-xs font-medium bg-green-50 text-green-700 border border-green-200 rounded-md">
            Current (Today) - {label}
          </span>
        </div>
        <div className="p-4 bg-green-50 border-2 border-green-200 rounded-lg text-sm leading-relaxed text-gray-800">
          {renderDiff(newWords, false)}
        </div>
      </div>
    </div>
  );
}
