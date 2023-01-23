# python-bitcask
This project attempts to implement [Bitcask](https://riak.com/assets/bitcask-intro.pdf) in Python. I may not implement the entire API; the goal of this project is honestly to re-build familiarity with Python after multiple years of mostly ops-focused SRE work. I may also deviate from the Bitcask architecture fairly quickly; for example, I may look into making the keydir sparse and using a memtable up-front so that the keys are always sorted (i.e. start with Bitcask but evolve into LSMTree). I also want to follow the excellent narrative that Martin Kleppman sets out in the Storage & Retrieval chapter of DDIA. Actually, that is a perfect starting point.

The simplest database looks like this. `set(key, value)` appends `key,value` to a file. `get(key)` scans that file and returns the last result (why last? because maybe we called `set` multiple times for the same key, and so we want to return the latest value). Let's discuss some of the properties of this database. Its memory usage is low; we only need to store chunks of the file in memory as we scan it during `get`. It has a fast startup time, since there is nothing to load on startup. `set` is extremely fast since disk appends are fast, and we don't need to update any in-memory (or otherwise) data structures. The problem is with `get`: we always have to scan the entire file in case the latest value for our key is at the end. That is, of course, completely unacceptable, but we'll improve that later. By the way, what I just outlined above are important performance characteristics for any database (not at all exhaustive, though): how fast are reads, how fast are writes, what is the memory usage, how long does startup take?

So, let's implement this thing. One thing: I tend to get really hung up on organisation, so for now I am going to start very simple and keep the hierarchy completely flat. Oh, and one more thing: so that I don't have to worry about working with binary files, to start I will allow only simple text keys and values.

Cool, that's done. See commit a2bd15. It's funny how much of programming is boring. For example, even this simplest implementation would benefit from command line validation (e.g. the value must be passed if we are doing a `set`), or other kinds of checks (when doing a `get`, make sure the file exists before trying to open it). I have left lots of that out because I am focused on more complex tasks which are more likely to need me to interface with the standard library.

OK, now, there *is* a way to improve the non-worst-case in the current approach: we can scan the file *backwards* and stop scanning once we've found our key. The worst case would not improve (we might still have to scan the entire file). Scanning a file backwards is fairly complex, as far as I know: you scan it N bytes at a time. Those N bytes may contain an entire key/value pair (which you will know because you found two newlines [why not one? because maybe you scanned a bit of the beginning of a key/value pair, followed by a newline, and then a bit of the end of a key/value pair, e.g. "oo\nba"]), in which case you can extract it and add the remainder to your buffer. Or, they may not, in which case you have to keep scanning. I mean, it seems like a pretty good exercise... let me try it. OK, I hacked away at it for a couple hours, and learned some stuff, but I'm not very interested in pursuing it to the end and using it in the database. If interested, check out the `dmitry/backwards-simplest-db` branch, or for an actual implementation of reading a file in reverse, see [this SO answer](https://stackoverflow.com/a/23646049/410963).

Hello! I am back. It's been a little while. I should be studying for a job interview tomorrow, but I'm not sure what to study, so instead I'll build my Python confidence by working on this. So, what's next? Let's say we _had_ implemented the reverse-reading store. What would its characteristics be?
* fast to start (doesn't need to load anything into memory)
* low memory usage (the only thing we load into memory is the current part of the datastore file that we are scanning)
* fast writes: still just append to a file
* slow reads: the reverse reading is not a huge improvement on the original; it just saves us from having to read the whole file *every* time

So, how can we improve on this? Remember that there is no free lunch in computing. You always have to trade something for something. What do we want to improve? The reads. And what can we spend to improve it? Note that the memory usage is extremely low, the writes are extremely fast, and the database is very fast to start. We have a lot of stuff we can trade. Here's one thing we can do.

How do databases make reads faster? Using an index. Without an index, database reads would always be slow as shit! How can we make finding a value in our datastore file faster? We can keep an in-memory dictionary mapping keys to the value locations in the data store! What would that look like, and what would we pay for it?

Here's what it would look like: the keys of the dictionary would be strings (because our datastore keys are strings) and the values would be integers corresponding to offsets in the source of truth datastore file (have I yet assigned it a name I can use to easily refer to it? let's call it the "datastore file"). Why don't we just store the values in this dictionary? Because the values could be big, and the store has one serious limitation: all our keys need to fit in memory. This is how Bitcask is actually implemented, but it's a pretty serious limitation.

That brings me to what we pay:
* memory usage is increased, because we now need to store keys and offsets in memory
* writes are slower, because when we write we need to add/update the entry in the dict
* the database is slower to start, because we need to load the dict

But what we get is much faster writes. How much faster? Well, look. Now, instead of scanning the entire file, all we need to do is fetch the offset, seek to it, and read. While seeking a lot is slow (IIRC a hard disk seek takes 10ms), it's a lot faster than reading the whole database all the time!

Let me try implementing it in a new branch called `dmitry/keydir`.

One thing I do need to understand here is how seeking works. Let's just say we are working with text files here, not binary files. I have two questions.
* When you call `write` does it return the number of characters written, or the number of bytes?
* When you call `seek` do you specify the number of characters, or the number of bytes?
I bet it's the number of characters. Let's try it. I'll create a file, and then write 'a😄️' to it. The a will take only 1 byte (any ascii char takes up 1 byte) and the smiley face will take more.

I just played around with this, and it makes _no_ sense. The Python docs *did* warn me: for text files, "write returns an opaque number".

In that case, what I have to do is work with binary files. I will need to decode the binary into a reasonable text encoding, and to prevent confusion I'll need to specify somewhere that it's UTF-8.

OK, now things make a lot more sense. Binary, it is.

Oh, one thing I forgot: the keydir needs to hold not just the offset, but also the length of the value to read. Otherwise, we don't know how much to read.