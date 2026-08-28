# Stretch goal note

I implemented the S2 stretch goal for saving and restoring a conversation.
I learned that the conversation history is just a list of message dictionaries,
so persisting it to JSON is straightforward once the data shape is validated.
