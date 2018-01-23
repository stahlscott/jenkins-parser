import sys
import xml.etree.ElementTree

BROKEN_INDICATORS = {'(broken'}
ABORTED_INDICATORS = {'(aborted)'}


def run(filename):
    file_root = get_jenkins_xml_from_file(filename)
    earliest_date = get_earliest_date(file_root)
    titles = parse_titles_from_rss(file_root)
    output_list = get_output_list(titles, earliest_date)
    print_output_list(output_list)


def get_jenkins_xml_from_file(filename):
    file_root = xml.etree.ElementTree.iterparse(filename)
    for _, el in file_root:
        if '}' in el.tag:
            el.tag = el.tag.split('}', 1)[1]
    root = file_root.root
    return root


def get_earliest_date(file_root):
    earliest_datetime = [entry[4].text for entry in file_root.findall('entry')][-1]
    earliest_date = earliest_datetime[:10]
    return earliest_date


def parse_titles_from_rss(file_root):
    titles = [entry[0].text for entry in file_root.findall('entry')]
    stripped_titles = [tl[tl.index(u'\xbb') + 2::] for tl in titles]
    return stripped_titles


def count_titles_matching_set(titles, matching_indicators):
    broken_titles = [t for t in titles if matching_indicators.intersection(set(t.split()))]
    return len(broken_titles)


def get_count_percentage_string(build_count, total_builds):
    percentage = float(build_count) / total_builds * 100
    return '{build_count} / {percentage:.2f}%'.format(build_count=build_count, percentage=percentage)


def get_output_list(titles, earliest_date):
    count_total_builds = len(titles)
    count_broken_builds = count_titles_matching_set(titles, BROKEN_INDICATORS)
    count_aborted_builds = count_titles_matching_set(titles, ABORTED_INDICATORS)
    count_passed_builds = count_total_builds - count_broken_builds - count_aborted_builds

    date_line = 'Since: {earliest_date}'.format(earliest_date=earliest_date)
    total_line = 'Total builds: {total}'.format(total=count_total_builds)
    broken_line = 'Broken: ' + get_count_percentage_string(count_broken_builds, count_total_builds)
    aborted_line = 'Aborted: ' + get_count_percentage_string(count_aborted_builds, count_total_builds)
    passed_line = 'Passed: ' + get_count_percentage_string(count_passed_builds, count_total_builds)
    line_break = '====='

    return [date_line, line_break, total_line, line_break, broken_line, aborted_line, passed_line]


def print_output_list(output_list):
    print('\n'.join(output_list))


if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print('XML file name is required as an argument\n'
              'exiting...')
        exit()
    run(filename=sys.argv[1])
