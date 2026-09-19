/* Independent compiler fingerprint: long_high_word_pointer */
recovered(v) long v; { return ((unsigned *)&v)[0]%3; }
