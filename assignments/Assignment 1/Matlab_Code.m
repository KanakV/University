%Input of Lamina P1 P2 P3 & radius
lamina = ones(4,3);
% disp("Enter points in format: [x y z]");
% for i = 1:3
%     lamina(i, 1:3) = input("[x y z]: ");
%     lamina(i, 4) = 1;
% end
% radius = input("Radius: ");

% For testing
lamina = [1 2 3 1;
          1 1 1 1;
          2 2 2 1];
radius = 0.2;


%Formation of circle matrix
t = linspace(0, pi, 100);
x = radius * cos(t);
y = radius * sin(t);
z = 0 * t;
q = ones(1, 100);
circle = [x; y; z; q]';

Q1 = zeros(1, 4);
Q = ones(1, 4);
Q1(1, :) = (lamina(1, :) + lamina(2, :)) / 2;

%Plot of Initial Positions
figure("Name","Intital position")
axis equal

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
legend("Lamina", "Circle", "Q1")
grid on
hold off

%Translating lamina to origin
translation = [1 0 0 0;
               0 1 0 0;
               0 0 1 0;
              -Q1(1) -Q1(2) -Q1(3) 1];
lamina = lamina * translation;

%Alignment of Lamina's Normal to z axis
n = cross(lamina(3, 1:3), lamina(2, 1:3));
n = n / norm(n);

%Cos & Sin terms for rotation
cx = n(3) / sqrt(1 - n(1)^2);
sx = n(2) / sqrt(1 - n(1)^2);
cy = sqrt(1 - n(1)^2);
sy = n(1);

%Rotation Matrices
Rx = [ 1  0  0  0;
       0  cx sx 0;
       0 -sx cx 0;
       0  0  0  1];

Ry = [ cy 0 sy 0;
       0  1  0  0;
      -sy 0  cy 0;
       0  0  0  1];

%Round to get rid of very small terms
lamina = round(lamina * Rx * Ry, 6);

%Plot of 
figure("Name", "Tranformed Lamina in XY plane")
axis equal
x = lamina(1:3,1);
y = lamina(1:3,2);
z = lamina(1:3,3);
fill3(x, y, z, 'g')
hold on
Q(1, :) = (lamina(1, :) + lamina(2, :)) / 2;
plot3(Q(1), Q(2), Q(3), 'r*')
X = circle(:, 1);
Y = circle(:, 2);
Z = circle(:,3);
fill3(X', Y', Z', "r")
legend("Lamina", "Circle", "Q1")
grid on
hold off

%Rotate Circle st OR coincident with OP1
cz = dot(circle(1, 1:3), lamina(1,1:3)) / (norm(circle(1, 1:3)) * norm(lamina(1,1:3)));
sz = sqrt(1 - cz^2);

Rz = [cz sz 0 0;
     -sz cz 0 0;
      0  0  1 0;
      0  0  0 1];
%Depending on where P1 is, rotation happens accordingly
if(lamina(1, 2) < 0)
    Rz = Rz';
end
circle = circle * Rz;

%Plot of Aligned figures
figure("Name","Alignment")
x = lamina(1:3,1);
y = lamina(1:3,2);
z = lamina(1:3, 3);
fill3(x',y',z', "g")
hold on
X = circle(:, 1);
Y = circle(:, 2);
Z = circle(:, 3);
fill3(X', Y', Z', "r")
Q(1, :) = (lamina(1, :) + lamina(2, :)) / 2;
plot3(Q(1), Q(2), Q(3), 'r*')
legend("Lamina", "Circle", "Q1")
grid on
hold off

%Undo Rotations
Rx = Rx';
Ry = Ry';
translation = [1 0 0 0;
               0 1 0 0;
               0 0 1 0;
              Q1(1) Q1(2) Q1(3) 1];
circle = round(circle * Ry * Rx * translation, 6);
lamina = lamina * Ry * Rx * translation;

%Display final output
figure("Name","Final Positions")
x = lamina(1:3,1);
y = lamina(1:3,2);
z = lamina(1:3, 3);
fill3(x',y',z', "g")
hold on
X = circle(:, 1);
Y = circle(:, 2);
Z = circle(:, 3);
fill3(X', Y', Z', "r")
Q(1, :) = (lamina(1, :) + lamina(2, :)) / 2;
plot3(Q(1), Q(2), Q(3), 'r*')
legend("Lamina", "Circle", "Q1")
grid on
hold off