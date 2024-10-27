// static/js/scripts.js

document.addEventListener("DOMContentLoaded", () => {
    const socket = io(); // Automatically connects to the host that serves the page

    // Metrics Elements
    const p1Elem = document.getElementById('p1');
    const p2Elem = document.getElementById('p2');
    const p3Elem = document.getElementById('p3');
    const irms1Elem = document.getElementById('irms1');
    const irms2Elem = document.getElementById('irms2');
    const irms3Elem = document.getElementById('irms3');
    const vrms1Elem = document.getElementById('vrms1');
    const vrms2Elem = document.getElementById('vrms2');
    const vrms3Elem = document.getElementById('vrms3');
    const downloadBtn = document.getElementById('downloadBtn');
    const alertsContainer = document.getElementById('alerts-container');

    // Define Electric Colors for Vibrant Charts
    const colors = {
        p1: 'rgba(0, 255, 255, 1)',      // Cyan
        p2: 'rgba(255, 165, 0, 1)',      // Orange
        p3: 'rgba(255, 0, 255, 1)',      // Magenta
        irms1: 'rgba(255, 215, 0, 1)',    // Gold
        irms2: 'rgba(75, 0, 130, 1)',     // Indigo
        irms3: 'rgba(173, 216, 230, 1)',  // LightBlue
        vrms1: 'rgba(255, 99, 71, 1)',    // Tomato
        vrms2: 'rgba(34, 139, 34, 1)',    // ForestGreen
        vrms3: 'rgba(0, 191, 255, 1)',    // DeepSkyBlue
        cost1: 'rgba(255, 165, 0, 1)',    // Orange for Cost
        cost2: 'rgba(75, 0, 130, 1)',     // Indigo for Cost
        cost3: 'rgba(173, 216, 230, 1)',  // LightBlue for Cost
        power1: 'rgba(0, 255, 255, 0.6)', // Semi-transparent Cyan
        power2: 'rgba(255, 165, 0, 0.6)', // Semi-transparent Orange
        power3: 'rgba(255, 0, 255, 0.6)'  // Semi-transparent Magenta
    };

    // Initialize Variables for Energy Consumption
    let energyConsumption = {
        ct1: 0, // in kWh
        ct2: 0,
        ct3: 0
    };
    let lastUpdateTime = Date.now();

    // Tariff Data
    const tariffData = [
        { tier: '0 – 300 kWh', tariff: 233.98, vat: 35.10 },
        { tier: '301 – 500 kWh', tariff: 282.35, vat: 42.35 },
        { tier: '>500 kWh', tariff: 318.41, vat: 47.76 }
    ];

    // Initialize Charts
    let powerChart, currentChart, voltageChart, costPieChart, powerPieChart, energyCostChart;
    initializeCharts();

    function initializeCharts() {
        // Initialize Active Power Chart
        const powerChartCtx = document.getElementById('powerChart').getContext('2d');
        powerChart = new Chart(powerChartCtx, {
            type: 'line',
            data: {
                labels: [], // Timestamps
                datasets: [
                    {
                        label: 'CT1',
                        data: [],
                        borderColor: colors.p1,
                        backgroundColor: colors.p1.replace('1)', '0.2)'),
                        fill: false,
                        tension: 0.3,
                        borderWidth: 2,
                        pointRadius: 0
                    },
                    {
                        label: 'CT2',
                        data: [],
                        borderColor: colors.p2,
                        backgroundColor: colors.p2.replace('1)', '0.2)'),
                        fill: false,
                        tension: 0.3,
                        borderWidth: 2,
                        pointRadius: 0
                    },
                    {
                        label: 'CT3',
                        data: [],
                        borderColor: colors.p3,
                        backgroundColor: colors.p3.replace('1)', '0.2)'),
                        fill: false,
                        tension: 0.3,
                        borderWidth: 2,
                        pointRadius: 0
                    }
                ]
            },
            options: getCommonLineOptions('Active Power (W)')
        });

        // Initialize Current RMS Chart
        const currentChartCtx = document.getElementById('currentChart').getContext('2d');
        currentChart = new Chart(currentChartCtx, {
            type: 'line',
            data: {
                labels: [], // Timestamps
                datasets: [
                    {
                        label: 'CT1',
                        data: [],
                        borderColor: colors.irms1,
                        backgroundColor: colors.irms1.replace('1)', '0.2)'),
                        fill: false,
                        tension: 0.3,
                        borderWidth: 2,
                        pointRadius: 0
                    },
                    {
                        label: 'CT2',
                        data: [],
                        borderColor: colors.irms2,
                        backgroundColor: colors.irms2.replace('1)', '0.2)'),
                        fill: false,
                        tension: 0.3,
                        borderWidth: 2,
                        pointRadius: 0
                    },
                    {
                        label: 'CT3',
                        data: [],
                        borderColor: colors.irms3,
                        backgroundColor: colors.irms3.replace('1)', '0.2)'),
                        fill: false,
                        tension: 0.3,
                        borderWidth: 2,
                        pointRadius: 0
                    }
                ]
            },
            options: getCommonLineOptions('Current RMS (A)')
        });

        // Initialize Voltage RMS Chart
        const voltageChartCtx = document.getElementById('voltageChart').getContext('2d');
        voltageChart = new Chart(voltageChartCtx, {
            type: 'line',
            data: {
                labels: [], // Timestamps
                datasets: [
                    {
                        label: 'CT1',
                        data: [],
                        borderColor: colors.vrms1,
                        backgroundColor: colors.vrms1.replace('1)', '0.2)'),
                        fill: false,
                        tension: 0.3,
                        borderWidth: 2,
                        pointRadius: 0
                    },
                    {
                        label: 'CT2',
                        data: [],
                        borderColor: colors.vrms2,
                        backgroundColor: colors.vrms2.replace('1)', '0.2)'),
                        fill: false,
                        tension: 0.3,
                        borderWidth: 2,
                        pointRadius: 0
                    },
                    {
                        label: 'CT3',
                        data: [],
                        borderColor: colors.vrms3,
                        backgroundColor: colors.vrms3.replace('1)', '0.2)'),
                        fill: false,
                        tension: 0.3,
                        borderWidth: 2,
                        pointRadius: 0
                    }
                ]
            },
            options: getCommonLineOptions('Voltage RMS (V)')
        });

        // Initialize Energy Cost Pie Chart
        const costPieChartCtx = document.getElementById('costPieChart').getContext('2d');
        costPieChart = new Chart(costPieChartCtx, {
            type: 'pie',
            data: {
                labels: ['CT1', 'CT2', 'CT3'],
                datasets: [{
                    label: 'Energy Cost (R)',
                    data: [0, 0, 0], // Initial data
                    backgroundColor: [
                        colors.cost1,
                        colors.cost2,
                        colors.cost3
                    ],
                    borderColor: '#ffffff', // White border for outline
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                        labels: {
                            color: '#ffffff'
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                let label = context.label || '';
                                if (label) {
                                    label += ': ';
                                }
                                if (context.parsed !== null) {
                                    label += `R${context.parsed.toFixed(2)}`;
                                }
                                return label;
                            }
                        }
                    },
                    datalabels: {
                        color: '#ffffff',
                        formatter: function(value, context) {
                            return value > 0 ? `R${value.toFixed(2)}` : '';
                        },
                        font: {
                            weight: 'bold',
                            size: 14
                        }
                    }
                },
                animation: {
                    animateRotate: true,
                    animateScale: true
                }
            },
            plugins: [ChartDataLabels]
        });

        // Initialize Total Power Consumption Pie Chart
        const powerPieChartCtx = document.getElementById('powerPieChart').getContext('2d');
        powerPieChart = new Chart(powerPieChartCtx, {
            type: 'pie',
            data: {
                labels: ['CT1', 'CT2', 'CT3'],
                datasets: [{
                    label: 'Power Consumption (W)',
                    data: [0, 0, 0], // Initial data
                    backgroundColor: [
                        colors.power1,
                        colors.power2,
                        colors.power3
                    ],
                    borderColor: '#ffffff', // White border for outline
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                        labels: {
                            color: '#ffffff'
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                let label = context.label || '';
                                if (label) {
                                    label += ': ';
                                }
                                if (context.parsed !== null) {
                                    label += `${context.parsed} W`;
                                }
                                return label;
                            }
                        }
                    },
                    datalabels: {
                        color: '#ffffff',
                        formatter: function(value, context) {
                            return value > 0 ? `${value} W` : '';
                        },
                        font: {
                            weight: 'bold',
                            size: 14
                        }
                    }
                },
                animation: {
                    animateRotate: true,
                    animateScale: true
                }
            },
            plugins: [ChartDataLabels]
        });

        // Initialize Energy Cost Bar Chart
        const energyCostChartCtx = document.getElementById('energyCostChart').getContext('2d');
        energyCostChart = new Chart(energyCostChartCtx, {
            type: 'bar',
            data: {
                labels: ['CT1', 'CT2', 'CT3'],
                datasets: [{
                    label: 'Energy Cost (R)',
                    data: [0, 0, 0],
                    backgroundColor: [
                        colors.cost1,
                        colors.cost2,
                        colors.cost3
                    ],
                    borderColor: '#ffffff',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                let label = context.dataset.label || '';
                                if (label) {
                                    label += ': ';
                                }
                                if (context.parsed.y !== null) {
                                    label += `R${context.parsed.y.toFixed(2)}`;
                                }
                                return label;
                            }
                        }
                    },
                    datalabels: {
                        anchor: 'end',
                        align: 'start',
                        color: '#ffffff',
                        formatter: function(value) {
                            return `R${value.toFixed(2)}`;
                        },
                        font: {
                            weight: 'bold',
                            size: 14
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Cost (R)',
                            color: '#ffffff'
                        },
                        ticks: {
                            color: '#ffffff'
                        },
                        grid: {
                            color: '#444'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'CT Sensors',
                            color: '#ffffff'
                        },
                        ticks: {
                            color: '#ffffff'
                        },
                        grid: {
                            color: '#444'
                        }
                    }
                },
                animation: {
                    duration: 1000,
                    easing: 'easeInOutQuart'
                }
            },
            plugins: [ChartDataLabels]
        });
    }

    // Function to get common line chart options
    function getCommonLineOptions(titleText) {
        return {
            responsive: true,
            animation: {
                duration: 1000,
                easing: 'easeInOutQuart'
            },
            interaction: {
                mode: 'nearest',
                intersect: false,
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        color: '#ffffff'
                    }
                },
                title: {
                    display: false,
                    text: titleText
                }
            },
            scales: {
                x: {
                    type: 'time',
                    time: {
                        parser: 'yyyy-MM-dd HH:mm:ss',
                        tooltipFormat: 'HH:mm:ss',
                        unit: 'minute',
                        displayFormats: {
                            minute: 'HH:mm'
                        }
                    },
                    grid: {
                        color: '#444'
                    },
                    title: {
                        display: true,
                        text: 'Time',
                        color: '#ffffff'
                    }
                },
                y: {
                    beginAtZero: true,
                    grid: {
                        color: '#444'
                    },
                    title: {
                        display: true,
                        text: 'Value',
                        color: '#ffffff'
                    },
                    ticks: {
                        color: '#ffffff'
                    }
                }
            }
        };
    }

    // Initialize Alert Tracking
    let activeAlerts = {};

    // Initialize Variables for Energy Cost
    let totalEnergyCost = {
        ct1: 0, // in R
        ct2: 0,
        ct3: 0
    };

    // Listen for updates from the server
    socket.on('update', (data) => {
        console.log('Received data:', data); // Debugging

        // Update metrics display
        p1Elem.textContent = `${data.p1} W`;
        p2Elem.textContent = `${data.p2} W`;
        p3Elem.textContent = `${data.p3} W`;
        irms1Elem.textContent = `${data.irms1} A`;
        irms2Elem.textContent = `${data.irms2} A`;
        irms3Elem.textContent = `${data.irms3} A`;
        vrms1Elem.textContent = `${data.vrms1} V`;
        vrms2Elem.textContent = `${data.vrms2} V`;
        vrms3Elem.textContent = `${data.vrms3} V`;

        // Update Status Indicators based on voltage and power
        // If voltage is negative or power <=2 W, show 'Disconnected'
        // Else, show 'Connected'
        updateStatus('ct1', data.vrms1, data.p1);
        updateStatus('ct2', data.vrms2, data.p2);
        updateStatus('ct3', data.vrms3, data.p3);

        // Calculate time elapsed since last update
        const currentTime = Date.now();
        const timeElapsed = (currentTime - lastUpdateTime) / 3600000; // in hours
        lastUpdateTime = currentTime;

        // Update energy consumption (kWh)
        energyConsumption.ct1 += (data.p1 > 2 ? data.p1 : 0) * timeElapsed / 1000; // W * h / 1000 = kWh
        energyConsumption.ct2 += (data.p2 > 2 ? data.p2 : 0) * timeElapsed / 1000;
        energyConsumption.ct3 += (data.p3 > 2 ? data.p3 : 0) * timeElapsed / 1000;

        // Calculate cost based on tariff
        calculateCost('ct1', energyConsumption.ct1);
        calculateCost('ct2', energyConsumption.ct2);
        calculateCost('ct3', energyConsumption.ct3);

        // Update Power Pie Chart
        updatePowerPieChart();

        // Update Alerts based on thresholds (Example: Power > 1000 W)
        checkAlerts(data);

        // Update Charts
        updateCharts(data);
    });

    // Function to Update Charts
    function updateCharts(data) {
        const timestamp = new Date(data.timestamp);

        // Active Power Chart
        powerChart.data.labels.push(timestamp);
        powerChart.data.datasets[0].data.push(data.p1 > 2 ? data.p1 : null); // CT1
        powerChart.data.datasets[1].data.push(data.p2 > 2 ? data.p2 : null); // CT2
        powerChart.data.datasets[2].data.push(data.p3 > 2 ? data.p3 : null); // CT3
        if (powerChart.data.labels.length > 100) { // Limit data points
            powerChart.data.labels.shift();
            powerChart.data.datasets.forEach((dataset) => {
                dataset.data.shift();
            });
        }
        powerChart.update();

        // Current RMS Chart
        currentChart.data.labels.push(timestamp);
        currentChart.data.datasets[0].data.push(data.irms1 > 0 ? data.irms1 : null); // CT1
        currentChart.data.datasets[1].data.push(data.irms2 > 0 ? data.irms2 : null); // CT2
        currentChart.data.datasets[2].data.push(data.irms3 > 0 ? data.irms3 : null); // CT3
        if (currentChart.data.labels.length > 100) { // Limit data points
            currentChart.data.labels.shift();
            currentChart.data.datasets.forEach((dataset) => {
                dataset.data.shift();
            });
        }
        currentChart.update();

        // Voltage RMS Chart
        voltageChart.data.labels.push(timestamp);
        voltageChart.data.datasets[0].data.push(data.vrms1 > 0 ? data.vrms1 : null); // CT1
        voltageChart.data.datasets[1].data.push(data.vrms2 > 0 ? data.vrms2 : null); // CT2
        voltageChart.data.datasets[2].data.push(data.vrms3 > 0 ? data.vrms3 : null); // CT3
        if (voltageChart.data.labels.length > 100) { // Limit data points
            voltageChart.data.labels.shift();
            voltageChart.data.datasets.forEach((dataset) => {
                dataset.data.shift();
            });
        }
        voltageChart.update();
    }

    // Function to Update Status Indicators
    function updateStatus(ct, voltage, power) {
        const statusElem = document.getElementById(`${ct}-status`);
        if (voltage < 0 || power <= 2) {
            statusElem.textContent = 'Disconnected';
            statusElem.classList.add('disconnected');
            statusElem.classList.remove('connected');
        } else {
            statusElem.textContent = 'Connected';
            statusElem.classList.add('connected');
            statusElem.classList.remove('disconnected');
        }
    }

    // Function to Calculate Cost Based on Tariff
    function calculateCost(ct, energy) {
        // Determine the tariff tier
        let tariff = 0;
        let vat = 0;
        if (energy <= 300) {
            tariff = 233.98;
            vat = 35.10;
        } else if (energy > 300 && energy <= 500) {
            tariff = 282.35;
            vat = 42.35;
        } else {
            tariff = 318.41;
            vat = 47.76;
        }

        // Total tariff per kWh in cents
        const totalTariffCents = tariff + vat;

        // Convert to Rands (assuming 100 cents = 1 Rand)
        const cost = (totalTariffCents / 100) * energy;

        // Update total energy cost
        totalEnergyCost[ct] = cost;

        // Update the pie chart and energy cost chart
        updateCostCharts();
    }

    // Function to Update Cost Charts
    function updateCostCharts() {
        // Update Energy Cost Pie Chart
        if (costPieChart) {
            costPieChart.data.datasets[0].data = [
                totalEnergyCost.ct1,
                totalEnergyCost.ct2,
                totalEnergyCost.ct3
            ];
            costPieChart.update();
        }

        // Update Energy Cost Bar Chart
        if (energyCostChart) {
            energyCostChart.data.datasets[0].data = [
                totalEnergyCost.ct1,
                totalEnergyCost.ct2,
                totalEnergyCost.ct3
            ];
            energyCostChart.update();
        }

        // Update Total Cost Display
        const totalCost = totalEnergyCost.ct1 + totalEnergyCost.ct2 + totalEnergyCost.ct3;
        document.getElementById('total-cost').textContent = `Total Cost: R${totalCost.toFixed(2)}`;
    }

    // Function to Update Power Pie Chart
    function updatePowerPieChart() {
        if (powerPieChart) {
            const ct1Power = parseFloat(document.getElementById('p1').textContent) || 0;
            const ct2Power = parseFloat(document.getElementById('p2').textContent) || 0;
            const ct3Power = parseFloat(document.getElementById('p3').textContent) || 0;
            const total = ct1Power + ct2Power + ct3Power;

            powerPieChart.data.datasets[0].data = [
                ct1Power,
                ct2Power,
                ct3Power
            ];
            powerPieChart.update();

            // Update Total Power Display
            document.getElementById('total-power').textContent = `Total Power Consumption: ${total} W`;
        }
    }

    // Function to Update Alerts and Notifications
    function checkAlerts(data) {
        // Example Alert: If any power exceeds 1000 W
        if (data.p1 > 1000) {
            addAlert('High Power Usage on CT1!', 'warning', 'high_power_ct1');
        }
        if (data.p2 > 1000) {
            addAlert('High Power Usage on CT2!', 'warning', 'high_power_ct2');
        }
        if (data.p3 > 1000) {
            addAlert('High Power Usage on CT3!', 'warning', 'high_power_ct3');
        }

        // Example Alert: Voltage drops below 110 V
        if (data.vrms1 < 110) {
            addAlert('Voltage Low on CT1!', 'info', 'low_voltage_ct1');
        }
        if (data.vrms2 < 110) {
            addAlert('Voltage Low on CT2!', 'info', 'low_voltage_ct2');
        }
        if (data.vrms3 < 110) {
            addAlert('Voltage Low on CT3!', 'info', 'low_voltage_ct3');
        }

        // Example Alert: Total Cost exceeds a certain threshold
        const totalCost = totalEnergyCost.ct1 + totalEnergyCost.ct2 + totalEnergyCost.ct3;
        if (totalCost > 10) { // R10 threshold
            addAlert('Total Energy Cost Exceeded R10!', 'warning', 'total_cost_exceeded');
        }
    }


    // Function to Add Alert
    function addAlert(message, type, alertId) {
        // Check if alert is already active
        if (activeAlerts[alertId]) {
            return; // Do not display the alert again
        }

        const alertDiv = document.createElement('div');
        alertDiv.classList.add('alert');
        if (type === 'success') {
            alertDiv.classList.add('success');
        } else if (type === 'info') {
            alertDiv.classList.add('info');
        } else if (type === 'warning') {
            alertDiv.classList.add('warning');
        }

        alertDiv.innerHTML = `
            <span>${message}</span>
            <button class="close-btn">&times;</button>
        `;

        alertsContainer.appendChild(alertDiv);

        // Mark the alert as active
        activeAlerts[alertId] = true;

        // Add event listener to close button
        const closeBtn = alertDiv.querySelector('.close-btn');
        closeBtn.addEventListener('click', () => {
            alertsContainer.removeChild(alertDiv);
            delete activeAlerts[alertId]; // Remove alert from active alerts
        });
    }

    // Function to Handle Download Button Click
    downloadBtn.addEventListener('click', () => {
        window.location.href = '/download';
    });
});
