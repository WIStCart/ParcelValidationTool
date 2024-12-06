import { testValues } from "./summary.js";

const rawData = testValues.Fields_Diffs

const data = {
    labels: [],
    datasets: [{
        data: []
    }]
};

for (const key in rawData) {
    data.labels.push(key);
    data.datasets[0].data.push(parseFloat(rawData[key]));
}

const threshold = 15;

export const filteredData = {
    labels: data.labels.filter((_, index) => Math.abs(data.datasets[0].data[index]) >= threshold),
    datasets: [
        {
            label: "15% or more increase in records",
            data: data.datasets[0].data.filter(value => value > threshold),
            backgroundColor: barColor(),
            borderColor: borderColor(),
            borderWidth: 1,
        }, {
            label: "15% or more decrease in records",
            data: replicate([0], data.datasets[0].data.filter(value => value > threshold).length).concat(data.datasets[0].data.filter(value => value < -threshold)),
            backgroundColor: barColor(),
            borderColor: borderColor(),
            borderWidth: 1,
        }
    ]
};

function replicate(a, n) { return !n ? [] : replicate(a, n-1).concat(a); }

function barColor() {
    return(ctx) => {
        console.log(ctx)
        const standard = 0;
        const differences = ctx.raw;
        const color = differences > standard ? 'rgba(75, 192, 192, 0.2)' : differences <= standard ? 'rgba(255, 26, 104, 0.2)' : 'black';

        return color;
    }
}

function borderColor() {
    return(ctx) => {
        console.log(ctx)
        const standard = 0;
        const differences = ctx.raw;
        const color = differences > standard ? 'rgba(75, 192, 192, 1)' : differences <= standard ? 'rgba(255, 26, 104, 110.2)' : 'black';

        return color;
    }
}