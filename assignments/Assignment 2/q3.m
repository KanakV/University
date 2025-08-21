% For Testing
% n = 3;
% P = [0  0  1;
%      1  2  0;
%      3  2  0;
%      6 -1  0;]; 

%Inputs
n = 0;
while(~(n > 0))
    disp("Enter the degree of curve");
    n = input("n: ");
end

P = zeros(n+1, 3);

disp("Enter the control points (n+1 points)");
for i = 1 : n+1
    P(i, :) = input("[x y z]: "); 
end

%Original Curve
u = linspace(0, 1);
B = bernsteinMatrix(n, u);

r = B * P;


% New Geometric Coeff
newP = zeros(n+2, 3);
newP(1, :) = P(1, :);
newP(n+2, :) = P(n+1, :);

for i = 1:n
    newP(i+1, :) = (1 - i/(n+1)) * P(i+1,:) + (i/(n+1)) * P(i, :); 
end

% New Bernstein
newB = bernsteinMatrix(n+1, u);
newr = newB * newP;


% Figures
figure
title('Degree Elevation of Bezier Curve')
plot3(r(:, 1), r(:, 2), r(:, 3));
hold on 
scatter3(P(:, 1), P(:, 2), P(:, 3), 'b*')
plot3(P(:, 1), P(:, 2), P(:, 3), 'b--')
scatter3(newP(:, 1), newP(:, 2), newP(:, 3), 'r*')
plot3(newP(:, 1), newP(:, 2), newP(:, 3), 'r--')

legend('Bezier Curve', 'Original Control Points', '', 'New Control Points', '')