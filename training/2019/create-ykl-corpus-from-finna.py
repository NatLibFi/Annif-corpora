
import sys
import json


def main(ndjson_in):
    """Prints the title (nimike) and subjects (aiheet) contained in the json
    objects of the input."""
    for ind, line in enumerate(ndjson_in):
        line_dict = json.loads(line)
        if (
            not 'title' in line_dict.keys()
            or not 'classifications' in line_dict.keys()
            #or not 'subjectsExtended' in line_dict.keys()
           
        ):
            continue
        


        subjects = line_dict['classifications']

        if subjects:
        #if get_subjects(line_dict['subjectsExtended']) == True:
            try:
                print_title_with_subject_uris(line_dict['title'], (line_dict['classifications']['ykl']))
                #print(line_dict['title'] + '\t' + '\t'.join(line_dict['classifications']['ykl']))
            except KeyError:
                print('not found')
            except TypeError:
                print('not found')    


def print_title_with_subject_uris(title, subjects):
    urilist = [label for label in subjects]
    urilist = [uri for uri in urilist if uri is not None]
    urilist = [u for u in urilist if is_uri_number(u)]
    print(title + '\t' + '\t'.join(
         ['<http://urn.fi/URN:NBN:fi:au:ykl:'+item+'>' for item in urilist]
    ))

#Check if uri is a number
def is_uri_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

               


#%%
#%%
if __name__ == '__main__':
    # QUESTION: Which way stdin is expected?
    if sys.stdin.isatty():  # When no redirected input from file
        # Print instructions and wait for input if not redirected input?
        print('No redirected stdin data from file found. '
              'Example usage with input and output data files:\n'
              '\t$ python extract_subjects.py < file_in.ndjson > file_out.tsv'
              '\n\nWaiting for input:')
        sys.exit()
    main(sys.stdin)








































