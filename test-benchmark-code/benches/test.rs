use criterion::{criterion_group, criterion_main, Criterion};

pub fn test_benchmark(c: &mut Criterion) {
    let mut group = c.benchmark_group("assembly");
    group.sample_size(20);

    for i in [10, 30] {
        group.bench_function(&format!("Add {i} numbers"), |b| {
            b.iter(|| {
                let mut value = 0;
                for j in 1..i + 1 {
                    value += j;
                }
                value
            })
        });
    }
    group.finish();
}

criterion_group!(benches, test_benchmark);
criterion_main!(benches);
