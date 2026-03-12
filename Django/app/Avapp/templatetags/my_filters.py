from django import template

register = template.Library()

@register.filter
def get(dictionary, key):
    """Get the value of a key from a dictionary."""
    return dictionary.get(key, None)


@register.filter
def split_taxonomy(taxonomy_string):
    taxonomy_list = taxonomy_string.split(";")

    # Create an empty string to store the formatted taxonomy
    formatted_taxonomy = ""

    # Loop through each key-value pair in the dictionary
    for key, value in {
        'domain': taxonomy_list[0],
        'phylum': taxonomy_list[1],
        'class': taxonomy_list[2],
        'order': taxonomy_list[3],
        'family': taxonomy_list[4],
        'genus': taxonomy_list[5],
        'species': taxonomy_list[6]
    }.items():
        # Add the key and value to the formatted string
        formatted_taxonomy += f"{key}: {value}<br>"

    # Return the formatted string
    return formatted_taxonomy
#
# def split_taxonomy(taxonomy_string):
#     taxonomy_list = taxonomy_string.split(";")
#     formatted_taxonomy = []
#
#     # Loop through each key-value pair in the dictionary
#     for key, value in {
#         'domain': taxonomy_list[0],
#         'phylum': taxonomy_list[1],
#         'class': taxonomy_list[2],
#         'order': taxonomy_list[3],
#         'family': taxonomy_list[4],
#         'genus': taxonomy_list[5],
#         'species': taxonomy_list[6]
#     }.items():
#         # Append the formatted key-value pair to the list
#         formatted_taxonomy.append(f"{key}: {value}")
#
#     # Return the list of formatted key-value pairs
#     return formatted_taxonomy

@register.filter
def unique_taxonomies(taxonomies):
    seen_taxonomies = set()
    unique_list = []

    for taxonomy in taxonomies:
        if taxonomy not in seen_taxonomies:
            unique_list.append(taxonomy)
            seen_taxonomies.add(taxonomy)

    return unique_list


@register.filter
def remove_duplicates(input_list):
    seen = set()
    unique_list = []

    for item in input_list:
        if item not in seen:
            unique_list.append(item)
            seen.add(item)

    return unique_list
