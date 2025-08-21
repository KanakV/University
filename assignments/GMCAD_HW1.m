%Input of Lamina P1 P2 P3
lamina = ones(4,3);
for i = 1:3
    lamina(i, 1) = input("x: ");
    lamina(i, 2) = input("y: ");
    lamina(i, 3) = input("z: "); 
end

% For testing:
% lamina = [0 0 1 1;
%           1 0 0 1;
%           0 0 0 1];
% radius = 0.2;

%Input Radius
radius = input("Radius: ");

%Formation of circle
t = linspace(0, pi, 100);
x = radius * cos(t);
y = radius * sin(t);
z = 0 * t;
q = ones(1, 100);
circle = [x; y; z; q]';



%Finding Q1 & Plotting on previous Plot
Q1 = zeros(1,4);
Q1(1, :) = (lamina(1, :) + lamina(2, :)) / 2;

%Plot of Lamina, with Q1
figure("Name","Lamina at intital position")
axis equal
xlabel('x')
ylabel('y')
zlabel('z')
x = lamina(1:3,1);
y = lamina(1:3,2);
z = lamina(1:3,3);
fill3(x,y,z, 'g')
hold on
X = circle(:, 1);
Y = circle(:, 2);
Z = circle(:,3);
fill3(X', Y', Z', "r")
plot3(Q1(1), Q1(2), Q1(3), 'r*')
hold off

%Translating lamina to origin
translation = [1 0 0 0;
               0 1 0 0;
               0 0 1 0;
              -Q1(1) -Q1(2) -Q1(3) 1];
lamina = lamina * translation;

%Alignment of Normal to z axis to transform lamina to xy plane
%Normal to Q1,P1 & O,R1
n = cross(lamina(1, 1:3), circle(1, 1:3));
n = n / norm(n);
nx = n(1);
ny = n(2);
nz = n(3);

%Cos & Sin terms for rotation
cx = nz / sqrt(1 - nx^2);
sx = ny / sqrt(1 - nx^2);

cy = sqrt(1 - nx^2);
sy = nx;

%Rotation Matrices
Rx = [ 1  0  0  0;
       0  cx sx 0;
       0 -sx cx 0;
       0  0  0  1];

Ry = [ cy 0 -sy 0;
       0  1  0  0;
       sy 0  cy 0;
       0  0  0  1];

%Transform circle to join lamina on xy plane
lamina = lamina * Rx * Ry;

%Plot of Figure on xy plane
figure("Name", "Tranformed lamina on xy plane")
axis equal
xlabel('x')
ylabel('y')
zlabel('z')
x = lamina(1:3,1);
y = lamina(1:3,2);
z = lamina(1:3,3);
fill3(x,y,z, 'g')
hold on
X = circle(:, 1);
Y = circle(:, 2);
Z = circle(:,3);
fill3(X', Y', Z', "r")
hold off

%Required Alignment of Semicirlce and lamina
%Angle B/W Q1P1 & OR
c = dot(lamina(1,1:3), circle(1,1:3)) / (norm(lamina(1,1:3)) * norm(circle(1,1:3)));
s = sqrt(1 - c^2);

%Rotation of circle about z axis for Q1P1 & OR alignment
Rz = [ c s 0 0;
      -s c 0 0;
       0 0 1 0;
       0 0 0 1];
 circle = circle * Rz';

%Alignment Normals
%normal is defined as p1p3 x p1p2 which gives same direction as p3 x p2 
% if Q1 is origin
nLamina = cross(lamina(3,1:3), lamina(2,1:3));
%For circle normal is 0 0 1

%Normals need to be in same direction (i.e. z coord should be +ve for both
%or negative
if(nLamina(3) < 0)
    R = [-1 0  0 0;
          0 -1 0 0;
          0 0  0 0;
          0 0  0 1];
end

circle = circle * R;

%Plot of figure
figure("Name","Alignment Complete")
x = lamina(1:3,1);
y = lamina(1:3,2);
%z = lamina(3,1:3);
fill(x',y', "g")
hold on
X = circle(:, 1);
Y = circle(:, 2);
fill(X, Y, "r")
hold off

%Undo rotations
%Update transformation matrices
Ry = Ry';
Rx = Rx';
translation = [1 0 0 0;
               0 1 0 0;
               0 0 1 0;
               Q1(1) Q1(2) Q1(3) 1];


lamina = lamina * Ry * Rx * translation;
circle = circle * Ry * Rx * translation;

%Display final outpu
figure("Name","Output")
x = lamina(1:3,1);
y = lamina(1:3,2);
z = lamina(1:3, 3);
fill3(x',y',z', "g")
hold on
X = circle(:, 1);
Y = circle(:, 2);
Z = circle(:,3);
fill3(X', Y', Z', "r")
plot3(Q1(1), Q1(2), Q1(3), 'r*')
hold off