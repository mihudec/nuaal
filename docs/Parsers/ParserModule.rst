.. _parser_module:

ParserModule
============

``ParserModule(object)``

This class represents the base object, from which other (vendor specific classes) inherit. This class provides basic set of functions which handle parsing of raw text outputs based on Python's  ``re`` module and *regex* strings provided by `Patterns` class.

The core idea behind ``ParserModule`` is that the complexity of various command outputs differ. Some outputs, such as *'show mac address-table'*  are simple enough to be handled by single *regex* pattern. On the other hand, some  outputs, such as *'show interfaces'* are way more complex and would require a very long and complex *regex patterns* to match. Also, every little change in the output would cause this pattern not to match. To avoid the usage of overly complex regex patterns, the parsing can be divided into two steps, or *levels*.  In the first *level*, the text output is 'pre-processed', for example the output of *show interfaces* is splitted to list of strings, where each string represents a single interface. In the second *level*, each of these strings can be processed using multiple patterns, resulting in final *dictionary* representing the interface. For some outputs, these two levels can "overlap", meaning that the first level can already return a *dictionary*, but some of the keys need to be 'post-processed' by the second level. A great example of such command is *'show vlan brief'*, where the first level returns a list of dictionaries with keys `["vlan_id", "name", "ports"]`. The value of "`"ports"` (which is a string of all ports assigned to this VLAN) can be further processed by second *level*, which converts this string to a list of individual ports.

**Base Functions**

- ``match_single_pattern(self, text, pattern)`` - This function tries to match a single *regex* ``pattern`` on given ``text`` *string*. This function operates in two 'modes': with or without *named groups* in regex pattern. If ``pattern`` contains at least one *named group* (for example ``r"^(?P<name_of_the_group>.*)"``), the function will return *list* of *dictionaries*, where each *dictionary* has `"name_of_the_group"` as key and whatever the ``.*`` matched as value. If `pattern` does not contain any *named group*, *list* of *strings* is returned, each string being one match of the pattern (basically ``re.findall(pattern=pattern, string=text)``).
- ``update_entry(self, orig_entry, new_entry)`` - This function simply updates *dict* ``orig_entry`` with *dict* ``new_entry``. The changes are made only for keys, that are not in the ``orig_entry`` or those, which value is ``None``. The updated *dictionary* is returned.
- ``match_multi_pattern(self, text, patterns)`` - This function uses multiple *regex* ``patterns`` to match against given ``text``. At the beginning, a new *dictionary* is created with *named groups* of ALL the patterns as keys and values ``None``. Each time one of the patterns matches, the resulting *dictionary* is updated.
- ``_level_zero(self, text, patterns)`` - This function tries to match a pattern from `patterns` until a match is found. Then based on the ``self.match_single_pattern(**kwargs)`` returns either list of strings, or list of dictionaries. This function is used either for matching *'simple'* outputs or for pre-processing (and post-processing) of more complex outputs.
- ``_level_one(self, text, command)`` - Given the command variable (which represents the command used to get output), it determines the *level* of the command and fetches corresponding *patterns* from ``self.patterns["level0"][command]`` (an instance of ``Patterns`` class). If the *level* is 0, it simply returns the output of ``self._level_zero(text, patterns)``. If the *level* is 1, it continues to process individual entries returned by ``_level_zero`` based on patterns from ``self.patterns["level1"][command]``. Return a list of dictionaries.
- ``autoparse(self, text, command)`` - The main entry point for parsing, given just the ``text`` output and ``command`` it determines the proper way to parse the output and returns result.


.. autoclass:: nuaal.Parsers.ParserModule
    :members:
    :undoc-members:
    :private-members:
    :show-inheritance:

.. autoclass:: nuaal.Parsers.CiscoIOSParser
    :members:
    :undoc-members:
    :private-members:
    :show-inheritance:
