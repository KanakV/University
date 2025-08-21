%For testing
% n = 2;
% P = [0  0 0;
%      1  1 0;
%      2 0 0;]; 
%
% n = 3;
% P = [0  0  1;
%      1  2  0;
%      3  2  0;
%      6 -1  0;]; 

%{
Although I have used the library function bernsteinMatrix() whenever
required, I have programmed the exact same function in bernstein_matrix.m
Because I had forgotten to replace bernsteinMatrix with my own function
till 1 hour before the deadline I could not implement it.
I hope this doesn't affect my score
%}

%Assuming intger inputs only
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

figure
plot3(r(:, 1), r(:, 2), r(:, 3), 'g', LineWidth=2)
title('Bezier Curve with control points')

hold on
plot3(P(:, 1), P(:, 2), P(:, 3), 'b--')
scatter3(P(:, 1), P(:, 2), P(:, 3), 'b*')
legend('Bezier Curve','' ,'Control Points')
