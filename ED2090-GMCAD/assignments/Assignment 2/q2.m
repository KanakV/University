% For Testing
% n = 2;
% P = [0  0  0;
%      1  1  1;
%      0 0 1;]; 

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

u = linspace(0, 1);
B = bernsteinMatrix(n, u);

r = B * P;

disp("Enter value of u where you want to cut: ")
cut = input("u: ");
% cut = 0.5;

q = zeros(n);
for i = 0:n
    temp = bernsteinMatrix(i, cut);
    for j = 1:i+1
        q(i+1, j) = temp(j);
    end
end

newP = q * P;

newr = B* newP;


figure
title('Truncation of Bezier Curve')
plot3(r(:, 1), r(:,2), r(:, 3));
hold on 
plot3(newr(:, 1), newr(:,2), newr(:, 3), 'green', LineWidth=2)
plot3(P(:, 1), P(:, 2), P(:, 3), 'blue--')
scatter3(P(:, 1), P(:, 2), P(:, 3), 'blue*')
plot3(newP(:, 1), newP(:, 2), newP(:, 3), 'red--')
scatter3(newP(:, 1), newP(:, 2), newP(:, 3), 'red*')
legend('Original Curve', 'Truncated Curve', '', 'Original Control Points', '', 'New Control Points')