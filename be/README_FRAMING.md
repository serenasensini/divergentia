Adapt the function to allow the editing of parts of speech according to the specified options. For example, if the user ask to change the font style or the font size to the nouns, the function should edit the sections' text accordingly. The input body should be like the following:

"
{
"highlighting": {
"enabled": false,
"color": "#FFFF00",
"nouns": false,
"verbs": false,
"adjectives": false,
"adverbs": false
}}
"

where, if the highlighting is enabled, the function should check which parts of speech are set to true and apply the specified color to those sections in the text. If the user wants to change the font style or size, the function should also check for those options and apply them to the relevant sections of the text. The function should be flexible enough to handle various combinations of options for different parts of speech.

Create different functions as utilities in the keyword service to recognize if the analyzed word is a noun, verb, adjective, or adverb. These functions can be used to determine which sections of the text should be edited based on the user's specified options. For example, you can create functions like `isNoun(word)`, `isVerb(word)`, `isAdjective(word)`, and `isAdverb(word)` that return true if the word belongs to the respective part of speech. 

Then, in the main function that processes the text, you can use these utility functions to check each word and apply the necessary formatting based on the user's preferences. For instance, if the user has enabled highlighting for nouns and set a specific color, you can loop through the text, check if each word is a noun using `isNoun(word)`, and apply the highlighting accordingly. 

Review also the implementation of the other functions to adapt to this new functionality to avoid duplicating code and ensure that the new features are integrated smoothly into the existing codebase. This may involve refactoring some of the existing functions to make them more modular and reusable, allowing for easier maintenance and scalability in the future.

Ensure to cover edge cases, such as when the user does not specify any options or when they specify conflicting options (e.g., enabling highlighting for both nouns and verbs but setting different colors for each). The function should handle these cases gracefully, perhaps by prioritizing certain options or providing default settings to ensure a consistent user experience. Furthermore, implement the whole workflow, starting from the route endpoint that receives the user's input, to the processing of the text based on the specified options, and finally to the output of the edited text with the applied formatting. This will ensure that the new functionality is fully integrated and functional within the existing system.