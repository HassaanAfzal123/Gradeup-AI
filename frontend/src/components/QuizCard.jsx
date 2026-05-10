import React from 'react';

const QuizCard = ({ question, selectedAnswer, onSelect }) => {
    const { id, question: questionText, options } = question;

    return (
        <div className="card animate-slideUp mb-4">
            <div className="mb-4">
                <h3 className="text-lg font-semibold text-neutral-800 mb-4">
                    Question {id}
                </h3>
                <p className="text-neutral-700 text-lg leading-relaxed">
                    {questionText}
                </p>
            </div>

            <div className="space-y-3">
                {options.map((option, index) => {
                    const isSelected = selectedAnswer === option;
                    const optionLabel = String.fromCharCode(65 + index); // A, B, C, D

                    return (
                        <label
                            key={index}
                            className={`
                flex items-center p-4 rounded-xl border-2 cursor-pointer
                transition-all duration-200 group
                ${isSelected
                                    ? 'border-primary bg-primary/10 shadow-md'
                                    : 'border-neutral-200 hover:border-primary/50 hover:bg-neutral-50'
                                }
              `}
                        >
                            <input
                                type="radio"
                                name={`question-${id}`}
                                value={option}
                                checked={isSelected}
                                onChange={() => onSelect(id, option)}
                                className="hidden"
                            />

                            <div
                                className={`
                  flex-shrink-0 w-6 h-6 rounded-full border-2 mr-4
                  flex items-center justify-center transition-all
                  ${isSelected
                                        ? 'border-primary bg-primary'
                                        : 'border-neutral-300 group-hover:border-primary'
                                    }
                `}
                            >
                                {isSelected && (
                                    <svg
                                        className="w-4 h-4 text-white"
                                        fill="currentColor"
                                        viewBox="0 0 20 20"
                                    >
                                        <path
                                            fillRule="evenodd"
                                            d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                                            clipRule="evenodd"
                                        />
                                    </svg>
                                )}
                            </div>

                            <div className="flex items-center flex-grow">
                                <span
                                    className={`
                    font-semibold mr-3 text-sm
                    ${isSelected ? 'text-primary' : 'text-neutral-500'}
                  `}
                                >
                                    {optionLabel}.
                                </span>
                                <span
                                    className={`
                    ${isSelected ? 'text-neutral-800 font-medium' : 'text-neutral-700'}
                  `}
                                >
                                    {option}
                                </span>
                            </div>
                        </label>
                    );
                })}
            </div>
        </div>
    );
};

export default QuizCard;
