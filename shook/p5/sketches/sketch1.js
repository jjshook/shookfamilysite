var s1 = function (p) {
   var img, imgLast, img1840, img1880, img1920;
   var imgHasChanged = false;
   var transparency = 255;

   p.setup = function () {
      var canvas = p.createCanvas(640, 250);
      canvas.mousePressed(p.doCanvasMousePressed);

      img = imgLast = img1840 = p.loadImage("p5/assets/1840_shook_surname.jpg");
      img1880 = p.loadImage("p5/assets/1880_shook_surname.jpg");
      img1920 = p.loadImage("p5/assets/1920_shook_surname.jpg");

      var but1840 = p.createButton("1840");
      but1840.mousePressed(p.changeButton1840);
      but1840.style("width: 100px; border-radius: 1px; margin-right: 8px");

      var but1880 = p.createButton("1880");
      but1880.mousePressed(p.changeButton1880);
      but1880.style("width: 100px; border-radius: 1px");

      var but1920 = p.createButton("1920");
      but1920.mousePressed(p.changeButton1920);
      but1920.style("width: 100px; border-radius: 1px; margin-left: 8px");
   }

   p.doCanvasMousePressed = function () {
      window.location.href = "http://www.ancestry.com/name-origin?surname=shook";
   }

   p.changeButtonAny = function (thisImg) {
      imgLast = img;
      img = thisImg;
      imgHasChanged = true;
   }

   p.changeButton1840 = function () {
      p.changeButtonAny(img1840);
   }

   p.changeButton1880 = function () {
      p.changeButtonAny(img1880);
   }

   p.changeButton1920 = function () {
      p.changeButtonAny(img1920);
   }

   p.draw = function () {
      if (imgHasChanged) {
         p.background(255);

         if (transparency > 0) {
            transparency -= 10;
         } else {
            imgHasChanged = false;
            imgLast = img;
            transparency = 255;
         }

         p.tint(255, transparency);
         p.image(imgLast, (p.width - imgLast.width) / 2, (p.height - imgLast.height) / 2);
      } else {
         p.image(imgLast, (p.width - imgLast.width) / 2, (p.height - imgLast.height) / 2);
      }
   }
}

new p5(s1, 'mySketch');
