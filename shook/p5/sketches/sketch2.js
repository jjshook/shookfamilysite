/* These sketches are associated with shook_1840_texas.html */

(function() {
   ////////////////////////////////////////////////////////////////////////////
   // SKETCH 1: Jacob Shook
   ////////////////////////////////////////////////////////////////////////////

   var s1 = function(p) {
      var xOrigin = 15.0;
      var yOrigin = 0.0;
      var canvasWidth = 640.0;
      var canvasHeight = 250.0;
      var rectWidth = 150.0;
      var rectHeight = 100.0;

      var rects = [
         { x: xOrigin,         y: (canvasHeight-rectHeight)/2-25,   width: rectWidth, height: rectHeight/3, "label":"Daniel Shook", "link":"http://shookfamily.org/shook/shook_daniel.html" },
         { x: xOrigin,         y: (canvasHeight-rectHeight)/2+25,   width: rectWidth, height: rectHeight/3, "label":"Jefferson Shook", "link":"http://shookfamily.org/shook/shook_jefferson.html" },
         { x: xOrigin,         y: (canvasHeight-rectHeight)/2+75,   width: rectWidth, height: rectHeight/3, "label":"Nathaniel Shook", "link":"http://shookfamily.org/shook/shook_nathaniel.html" },
         { x: xOrigin + 175.0, y: ((canvasHeight-rectHeight)/2)-65, width: rectWidth, height: rectHeight, "label":"Jacob Shook", "link":"http://shookfamily.org/shook/shook_nathaniel.html" },
         { x: xOrigin + 175.0, y: ((canvasHeight-rectHeight)/2)+65, width: rectWidth, height: rectHeight, "label":"Elizabeth Unknown", "link":"" }
      ];

      p.setup = function() {
         var canvas = p.createCanvas(640, 250);
      }

      function getRectIdx() {
         for (var i = 0; i < rects.length; i++)  {
            if (p.mouseX >= rects[i].x && p.mouseX <= (rects[i].x + rects[i].width + 1) && p.mouseY >= rects[i].y && p.mouseY <= (rects[i].y + rects[i   ].height + 1)) {
               return i;
            }
         }

         return -1;
      }

      p.mouseClicked = function() {
         switch (getRectIdx()) {
            case 0: window.location.href = "http://shookfamily.org/shook/shook_daniel.html"; break;
            case 1: window.location.href = "http://shookfamily.org/shook/shook_jefferson.html"; break;
            case 2: window.location.href = "http://shookfamily.org/shook/shook_nathaniel.html"; break;
            case 3: window.location.href = "http://shookfamily.org/shook/shook_jacob.html"; break;
            case 4: break;
            default: break;
         }
      }

      p.draw = function() {
         p.background(255);

         // Children
         for (var i = 0; i < 3; i++) {
            p.fill(128);
            p.rect(rects[i].x,rects[i].y,rects[i].width,rects[i].height);
            p.fill(255);
            p.textFont("Arial");
            p.textSize(12);
            p.text(rects[i].label, rects[i].x + 10, rects[i].y + 21);
         }

         // Father
         for (var i = 3; i < 5; i++) {
            p.fill(128);
            p.rect(rects[i].x,rects[i].y,rects[i].width,rects[i].height);
            p.fill(255);
            p.textFont("Arial");
            p.textSize(12);
            p.text(rects[i].label, rects[i].x + 10, rects[i].y + 55);
         }
      }
   }

   ////////////////////////////////////////////////////////////////////////////
   // SKETCH 2: Texas Counties
   ////////////////////////////////////////////////////////////////////////////

   var s2 = function(p) {
      var imgCurrent, imgLast;
      var imgHasChanged = false;
      var transparency = 255;
      var index = 0;

      var jsonArray = [
         { "label":"Daniel Shook\n1850 U.S. Census\nLamar County, Texas", "img":"p5/assets/states/tx/counties/lamar_county.jpg" },
         { "label":"Jefferson Shook\n1850 U.S. Census\nLiberty County, Texas", "img":"p5/assets/states/tx/counties/liberty_county.jpg" },
         { "label":"John Franklin Shook\n1850 U.S. Census\nCass County, Texas", "img":"p5/assets/states/tx/counties/cass_county.jpg" },
         { "label":"Josiah Shook\n1850 U.S. Census\nHarris County, Texas", "img":"p5/assets/states/tx/counties/harris_county.jpg" },
         { "label":"Nathaniel Shook\n1850 U.S. Census\nWalker County, Texas", "img":"p5/assets/states/tx/counties/walker_county.jpg" }
      ];

      var images = [];

      p.setup = function() {
         var canvas = p.createCanvas(640, 250);

         imgCurrent = imgLast = p.loadImage(jsonArray[0].img);

         for (var i in jsonArray)
         {
            images[i] = p.loadImage(jsonArray[i].img);
         }

         var but1 = p.createButton("<<");
         but1.mousePressed(previousButton);
         but1.style("width: 100px; border-radius: 1px; margin-right: 8px");

         var but2 = p.createButton(">>");
         but2.mousePressed(nextButton);
         but2.style("width: 100px; border-radius: 1px; margin-right: 8px");
      }

      function previousButton() {
         if (index == 0) { index = jsonArray.length - 1; } else { index--; }

         imgLast = imgCurrent;
         imgCurrent = jsonArray[index].img;
         imgHasChanged = true;
      }

      function nextButton() {
         if (index == jsonArray.length - 1) { index = 0; } else { index++; }

         imgLast = imgCurrent;
         imgCurrent = jsonArray[index].img;
         imgHasChanged = true;
      }

      p.draw = function() {
         p.background(255);

         if (imgHasChanged) {
            if (transparency > 0) {
               transparency -= 10;
            } else {
               imgHasChanged = false;
               imgLast = imgCurrent;
               transparency = 255;
            }
     
            p.tint(255, transparency);
            p.image(images[index], (p.width/2 - images[index].width) / 2, (p.height - images[index].height) / 2);
         } else {
            p.image(images[index], (p.width/2 - images[index].width) / 2, (p.height - images[index].height) / 2);
         }

         p.fill(0);
         p.textFont("Arial");
         p.textSize(12);
         p.text(jsonArray[index].label, p.width/2, 100);
      }
   }

   ////////////////////////////////////////////////////////////////////////////
   ////////////////////////////////////////////////////////////////////////////

   new p5(s1, 'mySketch1');
   new p5(s2, 'mySketch');
}());
