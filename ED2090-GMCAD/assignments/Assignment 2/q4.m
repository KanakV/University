% For Testing
% n = 2;
% points = [0 0 0;
%      1 1 0 ;
%      2 0 0;]; 
% n = 3;
% points = [0  0  1;
%      1  2  3;
%      3  2  0;
%      6 -1  -2;
%      2 3 1;]; 

% Inputs
n = 0;
while(~(n > 0))
    disp("Enter the degree of curve");
    n = input("n: ");
end

points = zeros(n+1, 3);

disp("Enter the control points (n+1 points)");
for i = 1 : n+1
    points(i, :) = input("[x y z]: "); 
end

u = linspace(0, 1);

%Tangent Vector
tangentBernstein = n * bernsteinMatrix(n-1, u);

newTangentpts = zeros(n, 3);

for i = 1 : n
    newTangentpts(i, :) = points(i+1, :) - points(i, :); 
end

tangent = tangentBernstein * newTangentpts;

%Normal Vector to curve
normalBernstein = n * (n - 1) * bernsteinMatrix(n-2, u);
newNormalpts = zeros(n-1, 3);

for i = 1:n-1
    newNormalpts(i, :) = points(i+2, :) - 2 * points(i+1, :) + points(i, :);
end

normal = normalBernstein * newNormalpts;

%Normal Vector to plane
planeNormal = cross(tangent, normal);

curvature = zeros(size(u, 2), 1);
%Finding Modulus
for i = 1:size(u, 2)
    curvature(i) = norm(planeNormal(i, :)) / (norm(tangent(i, :)))^3; 
end



% For Torsion
% We have already found out T, we need to find out third derivative

torsion = zeros(size(u, 2), 1);

if (n <= 2)
    
else
    B3 = n * (n - 1) * (n - 2) * bernsteinMatrix(n-3, u);
    newP3 = zeros((n-2), 3);
    for i = 1 : n-3
        newP3(i, :) = points(i+3, :) - 3 * points(i+2, :) + 3 * points(i+1, :) - points(i, :);
    end

    r3 = B3 * newP3;

    crossP = cross(tangent, r3);

    for i = 1:size(u, 2)
        torsion(i) = norm(crossP(i, :)) / (norm(tangent(i, :)))^2; 
    end
end

%Curve
B = bernsteinMatrix(n, u);
r = B * points;

figure
tiledlayout(3, 1)

nexttile
title('Bezier Curve')
plot3(r(:, 1), r(:, 2), r(:, 3), 'g', LineWidth=2)

nexttile
title('Curvature vs u')
plot(u, curvature);

nexttile
title('Torsion vs u')
plot(u, torsion);

