//---------------------------------------
// Program: line_test.cpp
// Purpose: Compare the speeds of four classic
//          line drawing algorithms.
// Author:  John Gauch
// Date:    March 2010
//---------------------------------------
#include <time.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include "timer.h"

// Define global variables
#define SIZE 1000
int Image[SIZE][SIZE];

//------------------------------------------------------------
// AI-GENERATED: Draw line using Midpoint line algorithm
//------------------------------------------------------------
void draw_midpoint_line(int x1, int y1, int x2, int y2, int value)
{
   int dx = abs(x2 - x1), sx = x1 < x2 ? 1 : -1;
   int dy = abs(y2 - y1), sy = y1 < y2 ? 1 : -1;
   int x = x1, y = y1;

   if (dx > dy)
   {
      int d = 2 * dy - dx;
      for (int i = 0; i <= dx; i++)
      {
         Image[y][x] = value;
         if (d > 0)
         {
            y += sy;
            d -= 2 * dx;
         }
         d += 2 * dy;
         x += sx;
      }
   }
   else
   {
      int d = 2 * dx - dy;
      for (int i = 0; i <= dy; i++)
      {
         Image[y][x] = value;
         if (d > 0)
         {
            x += sx;
            d -= 2 * dy;
         }
         d += 2 * dx;
         y += sy;
      }
   }
}

//------------------------------------------------------------
// AI-GENERATED: Approximate Xiaolin Wu's anti-aliased line
//------------------------------------------------------------
void draw_wu_line(int x0, int y0, int x1, int y1, int value)
{
   bool steep = abs(y1 - y0) > abs(x1 - x0);
   if (steep)
   {
      std::swap(x0, y0);
      std::swap(x1, y1);
   }
   if (x0 > x1)
   {
      std::swap(x0, x1);
      std::swap(y0, y1);
   }

   float dx = x1 - x0;
   float dy = y1 - y0;
   float gradient = (dx == 0) ? 1 : dy / dx;

   float y = y0 + 0.5;
   for (int x = x0; x <= x1; x++)
   {
      int px = steep ? (int)y : x;
      int py = steep ? x : (int)y;
      if (px >= 0 && py >= 0 && px < SIZE && py < SIZE)
         Image[py][px] = value;
      y += gradient;
   }
}

//------------------------------------------------------------
// Draw line in 2D image using y=mx+b line equation
//------------------------------------------------------------
void draw_line_equation(int x1, int y1, int x2, int y2, int value)
{
   int dx = (x2-x1);
   int dy = (y2-y1);

   // Handle slope (0..1)
   if (abs(dy) < abs(dx))
   {
      // Calculate line equation
      float m = (float)dy/(float)dx;
      float b = y1 - m * x1;

      // Draw pixels on line
      if (dx > 0)
         for (int x=x1; x<=x2; x++)
            Image[(int)(m * x + b + 0.5)][x] = value;
      else
         for (int x=x2; x<=x1; x++)
            Image[(int)(m * x + b + 0.5)][x] = value;
   }
   
   // Handle slope [1..inf)
   else 
   {
      // Calculate line equation
      float m = (float)dx/(float)dy;
      float b = x1 - m * y1;

      // Draw pixels on line
      if (dy > 0)
         for (int y=y1; y<=y2; y++)
            Image[y][(int)(m * y + b + 0.5)] = value;
      else
         for (int y=y2; y<=y1; y++)
            Image[y][(int)(m * y + b + 0.5)] = value;
   }
}

//------------------------------------------------------------
// Draw line in 2D image using simple DDA algorithm
//------------------------------------------------------------
void draw_simple_DDA(int x1, int y1, int x2, int y2, int value)
{
   // Calculate step size
   int length = max(abs(x2-x1),abs(y2-y1));
   float dx = (x2 - x1) / (float)length;
   float dy = (y2 - y1) / (float)length;

   // Draw pixels on line
   float x = x1 + 0.5;
   float y = y1 + 0.5;
   for (int i = 0; i <= length; i++)
   {
      Image[(int)y][(int)x] = value;
      x += dx;
      y += dy;
   }
}

//------------------------------------------------------------
// Draw line in 2D image using fast DDA algorithm
//------------------------------------------------------------
void draw_fast_DDA(int x1, int y1, int x2, int y2, int value)
{
   // Calculate step size
   int dx = x2 - x1;
   int dy = y2 - y1;
   int x, y;

   // Handle slope (0..1)
   if (abs(dy) < abs(dx))
   {
      float step = (float)dy / (float)dx;
      float y = y1 + 0.5;
  
      if (dx > 0)
         for (x=x1; x<=x2; x++, y += step)
            Image[(int)y][x] = value;
      else
         for (x=x1; x>=x2; x--, y -= step)
            Image[(int)y][x] = value;
   }

   // Handle slope [1..inf)
   else 
   {
      float step = (float)dx / (float)dy;
      float x = x1 + 0.5;

      if (dy > 0)
         for (y=y1; y<=y2; y++, x += step)
            Image[y][(int)x] = value;
      else
         for (y=y1; y>=y2; y--, x -= step)
            Image[y][(int)x] = value;
   }
}

//------------------------------------------------------------
// Draw line in 2D image using Bresenham's algorithm
//------------------------------------------------------------
void draw_bresenham(int x1, int y1, int x2, int y2, int value)
{
   // Calculate step size
   int dx = x2 - x1;
   int dy = y2 - y1;
   int adx = (dx > 0) ? dx : -dx;
   int ady = (dy > 0) ? dy : -dy;
   int x, y;

   // Handle slope (0..1)
   if (ady < adx)
   {
      // Draw line with dx > 0
      if (dx > 0)
      {
         int error = dx/2;
         int step = (dy > 0) ? 1 : -1;
         for (x=x1, y=y1; x<=x2; x++)
         {
            Image[y][x] = value;
            error -= ady;
            if (error < 0)
            {
               error += dx;
               y += step;
            }
         }
      }
      
      // Draw line with dx < 0
      else 
      {
         int error = -dx/2;
         int step = (dy > 0) ? 1 : -1;
         for (x=x1, y=y1; x>=x2; x--)
         {
            Image[y][x] = value;
            error -= ady;
            if (error < 0)
            {
               error -= dx;
               y += step;
            }
         }
      }
   }

   // Handle slope [1..inf)
   else 
   {
      // Draw line with dy > 0
      if (dy > 0)
      {
         int error = dy/2;
         int step = (dx > 0) ? 1 : -1;
         for (x=x1, y=y1; y<=y2; y++)
         {
            Image[y][x] = value;
            error -= adx;
            if (error < 0)
            {
               error += dy;
               x += step;
            }
         }
      }

      // Draw line with dy < 0
      if (dy < 0)
      {
         int error = -dy/2;
         int step = (dx > 0) ? 1 : -1;
         for (x=x1, y=y1; y>=y2; y--)
         {
            Image[y][x] = value;
            error -= adx;
            if (error < 0)
            {
               error -= dy;
               x += step;
            }
         }
      }
   }
}

//---------------------------------------
// Main program
//---------------------------------------
int main(int argc, char *argv[])
{
   // Declare local variables
   int x1[SIZE];
   int y1[SIZE];
   int x2[SIZE];
   int y2[SIZE];

   // Generate random lines
   for (int i = 0; i < SIZE; i++)
   {
      x1[i] = rand() % SIZE;
      y1[i] = rand() % SIZE;
      x2[i] = rand() % SIZE;
      y2[i] = rand() % SIZE;
   }

   // Test line drawing function
   Timer t;
   t.start_timer();
   for (int j = 0; j < SIZE; j++)
      for (int i = 0; i < SIZE; i++)
         draw_line_equation(x1[i], y1[i], x2[i], y2[i], i);
   t.end_timer();
   printf("Line equation: %d lines/sec\n", int(SIZE*SIZE/t.elapsed_cpu()));
   
   // Test line drawing function
   t.start_timer();
   for (int j = 0; j < SIZE; j++)
      for (int i = 0; i < SIZE; i++)
         draw_simple_DDA(x1[i], y1[i], x2[i], y2[i], i);
   t.end_timer();
   printf("Simple DDA:    %d lines/sec\n", int(SIZE*SIZE/t.elapsed_cpu()));
   
   // Test line drawing function
   t.start_timer();
   for (int j = 0; j < SIZE; j++)
      for (int i = 0; i < SIZE; i++)
         draw_fast_DDA(x1[i], y1[i], x2[i], y2[i], i);
   t.end_timer();
   printf("Fast DDA:      %d lines/sec\n", int(SIZE*SIZE/t.elapsed_cpu()));
   
   // Test line drawing function
   t.start_timer();
   for (int j = 0; j < SIZE; j++)
      for (int i = 0; i < SIZE; i++)
         draw_bresenham(x1[i], y1[i], x2[i], y2[i], i);
   t.end_timer();
   printf("Bresenham:     %d lines/sec\n", int(SIZE*SIZE/t.elapsed_cpu()));
   return 0;
}