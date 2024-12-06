import {Bar} from "react-chartjs-2";

import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend,
} from "chart.js";

import { filteredData } from "./fieldDiffs.js";

ChartJS.register(
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend
)

export const FieldDiffsBar = () => {
    const options = {
        responsive: true,
        scales: {
            y: {
                min: -100,
                max: 100,
                ticks: {
                    stepSize: 25
                },
                title: {
                    display: true,
                    text: '% change',
                },
                grid: {
                    color: (context) => {
                        console.log(context)
                        const zeroLine = context.tick.value;
                        const gridColor = zeroLine === 0 ? '#665' : '#ccc';
                        return gridColor;
                    }
                }
            }
        },
        legend: {
            labels: {
                
            }
        }
    }

    return <Bar options={options} data = {filteredData}/>;
}