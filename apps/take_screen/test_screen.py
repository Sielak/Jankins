from PIL import ImageGrab
im = ImageGrab.grab() 
im.save('C:\\jenkins\screen.png')
print("Screen saved in C:\\jenkins\screen.png")