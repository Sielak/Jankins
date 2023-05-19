from reportlab.pdfgen.canvas import Canvas
from pdfrw import PdfReader
from pdfrw.toreportlab import makerl
from pdfrw.buildxobj import pagexobj
from datetime import date

input_file = "my_file.pdf"
output_file = "my_file_with_data.pdf"

# Get pages
reader = PdfReader(input_file)
pages = [pagexobj(p) for p in reader.pages]


# Compose new pdf
canvas = Canvas(output_file)

# for page_num, page in enumerate(pages, start=1):

#     # Add page
#     canvas.setPageSize((page.BBox[2], page.BBox[3]))
#     canvas.doForm(makerl(canvas, page))

#     # Draw data
#     data_text = "Page %s of %s" % (page_num, len(pages))
#     x = 128
#     canvas.saveState()
#     canvas.setStrokeColorRGB(0, 0, 0)
#     canvas.setLineWidth(0.5)
#     canvas.line(66, 78, page.BBox[2] - 66, 78)
#     canvas.setFont('Times-Roman', 10)
#     canvas.drawString(page.BBox[2]-x, 65, data_text)
#     canvas.restoreState()

#     canvas.showPage()



# Add page
page = pages[3]
canvas.setPageSize((page.BBox[2], page.BBox[3]))
canvas.doForm(makerl(canvas, page))

# Draw data


po_list = [
    {'po_number': '123456', 'po_supplier': 'Supplier ABC', 'packages': '12', 'pallets': '1', 'weight': '120'},
    {'po_number': '654321', 'po_supplier': 'Supplier sldoifhsadfhsoaa', 'packages': '0', 'pallets': '1', 'weight': '120'},
    {'po_number': '654321', 'po_supplier': 'Supplier alskdfhusapdoifjwe[epfoj', 'packages': '1', 'pallets': '1', 'weight': '120'},
    {'po_number': '654321', 'po_supplier': 'Supplier asdkfuhsdoifia', 'packages': '2', 'pallets': '1', 'weight': '120'},
    {'po_number': '654321', 'po_supplier': 'Supplier wewf65dwffwe', 'packages': '3', 'pallets': '1', 'weight': '120'},
    {'po_number': '324873', 'po_supplier': 'Supplier df25sdf5efe56fef', 'packages': '4', 'pallets': '1', 'weight': '120'},
    {'po_number': '987432', 'po_supplier': 'Supplier sdfd25sdf5ew6', 'packages': '5', 'pallets': '1', 'weight': '120'},
    {'po_number': '563832', 'po_supplier': 'Supplier sf2sd5we5we', 'packages': '6', 'pallets': '1', 'weight': '120'},
    {'po_number': '124978', 'po_supplier': 'Supplier 35135', 'packages': '7', 'pallets': '1', 'weight': '120'},
    {'po_number': '684555', 'po_supplier': 'Supplier sifheoiufjweoifjewofjewofhweufhwfqofjewuri', 'packages': '12', 'pallets': '1', 'weight': '120'}
    ]
canvas.setFont('Helvetica', 8)


# if len(po_list) > 8:
#     y = 280
#     y2 = 280
#     for item in po_list[:8]:
#         canvas.drawString(55, y, "PO{0}".format(item))
#         y -= 10
#     for item in po_list[8:]:
#         canvas.drawString(110, y2, "PO{0}".format(item))
#         y2 -= 10
# else:
#     y = 280
#     for item in po_list:
#         canvas.drawString(55, y, "PO{0}".format(item))
#         y -= 10

# Data from user
address = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
name = 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'
country = 'cccccccccccccccccccccccccccccccccccccccc'
vehicle_number = "SL5833E"
trailer_number = "WA1111A"
# 1. Sender
canvas.drawString(55, 755, "HL DISTRIBUTION CENTER EUROPE sp. z o.o.")
canvas.drawString(55, 745, "al. Jana Nowaka-Jezioranskiego 1")
canvas.drawString(55, 735, "44-164 Kleszczów")
canvas.drawString(55, 725, "Poland")
# 2. Consignee
canvas.drawString(55, 690, "HL Display Nordic AB")
canvas.drawString(55, 680, "Bultgatan 12")
canvas.drawString(55, 670, "85350 Sundsvall")
canvas.drawString(55, 660, "Sweden")
# 3. Place of delivery of the goods
canvas.drawString(55, 625, "Sundsvall, Sweden")
# 4. Place and date taking over the goods
canvas.drawString(55, 585, f"Kleszczów, Poland {date.today()}")
# 6. PO numbers
y_6 = 500
for item in po_list:
    canvas.drawString(55, y_6, "PO{0}".format(item['po_number']))
    canvas.drawString(110, y_6, "{0}pll/{1}pkg".format(item['pallets'], item['packages']))
    canvas.drawString(165, y_6, "Plastik")
    canvas.drawString(210, y_6, item['po_supplier'][:25])
    canvas.drawString(400, y_6, str(item['weight']))
    y_6 -= 10
# 6 numer po 
# 7 pll/pkg 
# 8 na sztywno Plastik 
# 9 nazwa suppliera (może wychodzic na 10 
# 13. Sender’s instructions
canvas.drawString(55, 280, "Towary bedace przedmiotem wewnatrzwspólnotowej")
canvas.drawString(55, 270, "dostawy towarów zgodnie z warunkami okreslonymi w")
canvas.drawString(55, 260, "art.. 42 ustawy z dnia 11-03-2004r o podatku od")
canvas.drawString(55, 250, "towarów i uslug.")
# 16. Carrier
canvas.drawString(305, 695, address)
canvas.drawString(305, 685, name)
canvas.drawString(305, 675, country)
canvas.drawString(345, 667, vehicle_number)
canvas.drawString(420, 667, trailer_number)
# 21. Established in
canvas.drawString(55, 160, f"Kleszczów, Poland {date.today()}")


canvas.showPage()

canvas.save()