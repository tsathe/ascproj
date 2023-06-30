import collections
import csv
import pprint
import re
from fuzzywuzzy import process
from typing import List, Dict
import pandas as pd


def get_unis() -> (List[str], Dict[str, int]):
    """
    Get the list of unis and the number of publications for each
    :rtype: str
    """
    with open('unis.csv', 'r') as csvfile:
        uni_list = []
        uni_to_pub = {}
        reader = csv.reader(csvfile)
        for row in reader:
            uni_list.append(row[0])
            uni_to_pub[row[0]] = int(row[1])
    return uni_list[:400], uni_to_pub


def _normalize_name(name) -> str:
    """
    Normalize the name of a university
    :param str name:
    :rtype: str
    """
    norm = name.lower()
    norm = re.sub(
        r'( +at +)|( *of *)|(university)|(hospital)|(medical center)|(institution)|(school)|(medicine)',
        ' ',
        norm,
    )
    return norm.strip()


def process_unis(uni_list, uni_to_pub):
    """
    Process the list of unis
    :param List[str] uni_list:
    :param Dict[str, int] uni_to_pub:
    :return:
    """
    # Normalize unis
    uni_list_norm = [(uni, _normalize_name(uni)) for uni in uni_list]

    # Construct empty choices list - we will iterate through the
    # list of universities from highest to lowest number of publications
    # We'll normalize each one and then try to match it to the choices list
    #
    # If the normalized name is not in the choices list (i.e. there is
    # no match), we'll add it so that future universities can be matched to it
    # and map the original name to the normalized name
    #
    # If the normalized name is in the choices list, we'll map the original
    # name to the normalized name
    choices = []
    bad_to_good = collections.OrderedDict()
    for item, normalized_item in uni_list_norm:
        potential_match = process.extractOne(normalized_item, choices)
        if not potential_match or potential_match[1] < 90:
            bad_to_good[item] = normalized_item
            choices.append(normalized_item)
        else:
            bad_to_good[item] = potential_match[0]

    # print(bad_to_good)

    # Now that we have a mapping of original name to normalized name
    # we can count the number of publications for each normalized name
    norm_counts = collections.defaultdict(int)
    for uni, norm in bad_to_good.items():
        norm_counts[norm] += uni_to_pub[uni]

    # Now we can go through the list of universities again and get the
    # normalized name from the bad_to_good mapping and add the number of
    # publications to the final map.
    #
    # Once we see a normalized name we'll add it to the seen_norms set
    # so that we don't double count and we'll assign the total number
    # of normalized publications to the most common name for that
    # university pre-normalization.
    #
    # Example - if we have Hospital of University of Pennsylvania (100) and
    # University of Pennsylvania Hospital (90), we'll assign the total number
    # of publications to Hospital of University of Pennsylvania (190) and
    # skip University of Pennsylvania Hospital (as they normalize to the same
    # thing)

    final_map = collections.defaultdict(int)
    seen_norms = set()
    for uni in uni_list:
        norm = bad_to_good[uni]
        if norm not in seen_norms:
            final_map[uni] += norm_counts[norm]
            seen_norms.add(norm)

    # pprint.pprint(sorted(final_map.items(), key=lambda x: x[1], reverse=True))

   



def run():
    uni_list, uni_to_pub = get_unis()
    process_unis(uni_list, uni_to_pub)


if __name__ == '__main__':
    run()
