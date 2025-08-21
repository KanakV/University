n = 3;
u = linspace(0, 1, 4);

B = zeros(size(u, 2), n+1);
temp = zeros(1, n+1);
for i = 0:n
    temp = nchoosek(n, i) * ((1 - u) .^ (n - i) .* (u .^ i)); 
    B(:, i+1) = temp';
end

