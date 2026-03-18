from docx import Document
from docx.opc.constants import RELATIONSHIP_TYPE as RT

def extract_hyperlinks(doc_path):
    doc = Document(doc_path)
    lines = []
    
    for para in doc.paragraphs:
        line_text = ''
        
        # In python-docx, hyperlinks are stored as <w:hyperlink> nodes which aren't fully exposed in p.runs 
        # But we can access them via the XML of the paragraph
        
        # A simple way to get both text and links: iterate over paragraph's children in XML
        # But even simpler: doc.part.rels contains all relationships, including hyperlinks.
        # But associating them with paragraphs is tricky.
        
        # Let's do a naive approach using iter_inner_content():
        # Actually docx doesn't make hyperlink extraction easy. 
        # Let's just parse the word/document.xml and word/_rels/document.xml.rels manually.
        pass

import zipfile
import xml.etree.ElementTree as ET

def extract_docx_with_links(docx_path):
    # Namespace dictionary
    ns = {
        'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
        'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
    }
    
    with zipfile.ZipFile(docx_path) as zf:
        xml_content = zf.read('word/document.xml')
        rels_content = zf.read('word/_rels/document.xml.rels')
        
    # parse rels
    rels_tree = ET.fromstring(rels_content)
    rels = {}
    for rel in rels_tree.findall('.//{http://schemas.openxmlformats.org/package/2006/relationships}Relationship'):
        rels[rel.get('Id')] = rel.get('Target')
        
    tree = ET.fromstring(xml_content)
    
    paragraphs = []
    for p in tree.findall('.//w:p', ns):
        text_pieces = []
        for child in p:
            if child.tag == f"{{{ns['w']}}}r":
                t_nodes = child.findall('.//w:t', ns)
                for t in t_nodes:
                    if t.text:
                        text_pieces.append(t.text)
            elif child.tag == f"{{{ns['w']}}}hyperlink":
                rel_id = child.get(f"{{{ns['r']}}}id")
                link = rels.get(rel_id, '')
                # get text inside hyperlink
                t_nodes = child.findall('.//w:t', ns)
                link_text = "".join([t.text for t in t_nodes if t.text])
                if link:
                    text_pieces.append(f"{link_text} ({link})")
                else:
                    text_pieces.append(link_text)
                    
        paragraphs.append("".join(text_pieces))
        
    return '\n'.join(paragraphs)

text_with_links = extract_docx_with_links('doc.docx')
with open('doc_with_links.txt', 'w', encoding='utf-8') as f:
    f.write(text_with_links)

print("Extraction complete!")
