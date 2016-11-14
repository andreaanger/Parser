import re
import xml.etree.ElementTree as ET
from xml.dom import minidom

def prettify(elem):
    # Return a pretty-printed XML string for the Element.
    rough_string = ET.tostring(elem, 'UTF-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def imagerepl(match):
    img_link = match.group(2)
    img_link = '<image>/images/' + img_link + '</image>'
    return img_link

def weblinkrepl(match):
    web_link = match.group(2)
    web_link = '<link>' + web_link + '</link>'
    return web_link

def linkrepl(match):
    link_link = match.group(2).split("/")
    link_link = '<link>/links/' + link_link[-1] + '</link>'
    return link_link

def unescape(doc):
    infile = open(doc)
    text = infile.read()
    infile.close()
    
    text = re.sub(r'&amp;quot;', '"', text)
    text = re.sub(r'&amp;lt;', '<', text)
    text = re.sub(r'&amp;gt;', '>', text)
    text = re.sub(r'&lt;', '<', text)
    text = re.sub(r'&gt;', '>', text)
    text = re.sub(r'&amp;', '&', text)
    text = re.sub(r'&amp;amp;', '&', text)
    text = re.sub(r'&quot;','"' , text)
    
    text = re.sub(r'&ldquo;', '&rdquo;', text)
    text = re.sub(r'&rdquo;', '"', text)
    text = re.sub(r'&ndash;', '_', text)
    text = re.sub(r'&rsquo;', "'", text)
    text = re.sub(r'&lsquo;', "'", text)
    text = re.sub(r'&copy;', "©", text)
    
    text = re.sub(r'<SDFIELD.*?></SDFIELD>', "", text)
    text = re.sub(r'<A\sNAME.*?>', "", text)
    with open("TEST.xml", "w", encoding = "utf8") as xml_file:
            print(text, file=xml_file)


def main():       
    infile = open("Computer_Basics.html", encoding="utf-8")
    html_source = infile.read()
    infile.close()

    # Finds all image links and adds tags
    html_source = re.sub(r'(<IMG\sSRC=")(.*?\.*\w+)(".*?>)', imagerepl, html_source)

    # Finds all web links and adds tags
    html_source = re.sub(r'(<A\sHREF=")(http.*?\.*\w+)(".*?>)', weblinkrepl, html_source)

    # Finds all local links and adds tags
    html_source = re.sub(r'(<A\sHREF=")(.*?\.*\w+)(".*?>)', linkrepl, html_source)
    
    # Removes all tags except image and link
    parse_tags = re.sub(r'<(P|FONT|SPAN|U|UL|B|LI|!DOC|HTML|HEAD|META|DIV|TITLE).*?>', '', html_source) 
    # Removes all closing tabs
    parse_closing = re.sub(r'</(P|FONT|SPAN|U|UL|B|LI|!DOC|HTML|HEAD|META|DIV|TITLE|I|A).*?>', '', parse_tags)
    raw_text = re.sub(r'<I>', '', parse_closing)

    length = len(raw_text)
##    print("Doc length is " + str(length))

    top_sections = ['Estimated\nTime:', 'Instructions:', 'Purpose:', 'SECTION\n1']
    remove_meta = raw_text.find('</STYLE>')
    startStop = []
    startStop.append(remove_meta+9)
    num = 0

    for item in top_sections:
        element = raw_text.find(top_sections[num])
        if element >= 0:
            startStop.append(element)
            num = num + 1
    
##    print("start points for header sections: " + str(startStop[0:5]))

    text_course_title = raw_text[startStop[0]:startStop[1]]
    text_est_time = raw_text[startStop[1]+16:startStop[2]]
    text_instructions = raw_text[startStop[2]+14:startStop[3]]
    text_purpose = raw_text[startStop[3]+9:startStop[4]]

    root = ET.Element("xml")
    #constant elements in every check sheet
    course_title = ET.SubElement(root, "course_title")
    course_title.text = text_course_title.strip()

    header = ET.SubElement(root, "header")
    est_time = ET.SubElement(header, "est_time")
    est_time.text = text_est_time.strip()

    instructions = ET.SubElement(header, "instructions")
    instructions.text = text_instructions.strip()

    purpose = ET.SubElement(header, "purpose")
    purpose.text = text_purpose.strip()

    #loop through sections
    # Finds the point that each section starts
    sections = ['SECTION\n1', 'SECTION\n2', 'SECTION\n3', 'SECTION\n4', 'SECTION\n5',
                'SECTION\n6', 'SECTION\n7', 'SECTION\n8', 'SECTION\n9', 'SECTION\n10',
                'SECTION\n11', 'SECTION\n12', 'SECTION\n13', 'SECTION\n14', 'SECTION\n15',
                'SECTION\n16', 'SECTION\n17', 'SECTION\n18', 'SECTION\n19', 'SECTION\n20',]

    startStop_seg = []
    num = 0
    for item in sections:
        element = raw_text.find(sections[num])
        if element >= 0:
            startStop_seg.append(element)
            num = num + 1
    
    startStop_seg.append(length)
##    print("section start points are: " + str(startStop_seg[0:-1]))

    numOfSections = len(startStop_seg) - 1
##    print("Sections: " + str(numOfSections)) # THIS IS FOR TESTING
    section_num = 1
    seg = 0
    while numOfSections > 0:
##        print("This is the start of SECTION " + str(section_num))

        # Creates the section tag
        section_name = "section_" + str(section_num)
        section_name = ET.SubElement(root, section_name)
        seg_end = seg + 1
        if section_num < 10:
            section_content = raw_text[startStop_seg[seg]+10:startStop_seg[seg_end]]
        else:
            section_content = raw_text[startStop_seg[seg]+11:startStop_seg[seg_end]]

        # Creates the section title tag
        end_title = section_content.find('Q1.')
        text_section_title = ' '.join(section_content[0:end_title].split())
        section_title = ET.SubElement(section_name, "section_title")
        section_title.text = text_section_title

        # Creates the section questions tag
        section_questions = ET.SubElement(section_name, "section_questions")

        # Finds start points of each question
        q = re.compile(r'\n+Q\d+\.')
        q_start = []
        for question in q.finditer(section_content):
            q_start.append(question.start())
        q_total = len(q_start)
##        print(str(q_total) + " unfiltered q start points")
##        print(q_start)
        current = 0

        seg_start = 0
        seg_stop = seg_start + 1
        i = 1

        q_start.append(len(section_content))


        # Creates tag for each question
        i = 1
        while len(q_start) >= 2:
            for item in q_start:
##                print("yeah! " + str(i))
                q_num = "q" + str(i)
                q_num = ET.SubElement(section_questions, q_num)
                q_text = section_content[q_start[0]:q_start[1]]
##                print("START SNIPPET for kept QUESTIONS: " + section_content[q_start[0]:q_start[0]+30])
                q_num.text = q_text.strip()             
                q_start.pop(0)
                i += 1
                seg_start += 1
            
        # Loop through to next section
##        print("End of SECTION " + str(section_num) + "\n\n")
        section_num = section_num + 1
        numOfSections = numOfSections - 1
        seg = seg + 1
        
    root = prettify(root)

    
    with open("TEST.xml", "w", encoding = "utf8") as xml_file:
        print(root, file=xml_file)

    unescape("TEST.xml")
    print("Parse Completed!")

main()
